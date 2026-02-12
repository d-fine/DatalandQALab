"""Compare NG flows (old vs new) and write an Excel report.

What it does
- For each dataset_id in a text file, this script calls:
  - OLD flow endpoint: /review/{data_id}
  - NEW flow endpoint: /data-point-flow/review-dataset/{data_id}
- It normalizes both responses and compares them against the NEW flow's `previous_answer`
  (treated as "Dataland truth").
- NEW "hit": predicted_answer == previous_answer
- OLD "hit": derived from qa_status (QaAccepted => match, QaRejected => mismatch)
- Produces an .xlsx with:
  - summary_overall, summary_by_dataset
  - results_by_datapoint, pivot_by_datapoint_key
  - mismatches_vs_dataland


How to use (local dev)
1) Create a txt file with one dataset_id per line, e.g.:
   data/txt/ng_ids_50.txt

2) Create output folder (terminal 2):
   mkdir out

3) Start the API locally (terminal 1):
   pdm run dev

4) Run the comparison script (terminal 2):
   pdm run python -m dataland_qa_lab.bin.compare_ng_flows --base-url http://127.0.0.1:8000 --ids-file data/txt/ng_ids_50.txt --out out/ng_compare.xlsx

"""  # noqa: E501

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
import pandas as pd
from dotenv import load_dotenv

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]

logger = logging.getLogger(__name__)

VOLATILE_KEYS = {
    "timestamp",
    "request_id",
    "trace_id",
    "span_id",
    "duration",
    "latency_ms",
    "processing_time_ms",
    "created_at",
    "updated_at",
}

HTTP_OK_MIN = 200
HTTP_OK_MAX = 300


def _auth_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    token = os.getenv("NG_AUTH_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _build_payloads(cfg: Config) -> tuple[dict[str, JsonValue], dict[str, JsonValue]]:
    old_payload: dict[str, JsonValue] = {
        "force_review": cfg.force_review,
        "ai_model": cfg.ai_model,
        "use_ocr": cfg.use_ocr,
    }
    new_payload: dict[str, JsonValue] = {
        "ai_model": cfg.ai_model,
        "use_ocr": cfg.use_ocr,
        "override": cfg.override,
    }
    return old_payload, new_payload


def _patch_old_error(old_res: CallResult) -> CallResult:
    """Mark old_res as failed if old flow returned an error object inside the report."""
    body = old_res.body
    raw_old: JsonValue = body.get("data") if isinstance(body, dict) and "data" in body else body
    old_report = raw_old.get("report") if isinstance(raw_old, dict) and "report" in raw_old else raw_old

    if isinstance(old_report, dict) and "error" in old_report:
        return CallResult(
            ok=False,
            status_code=old_res.status_code,
            latency_ms=old_res.latency_ms,
            body=old_res.body,
            error=str(old_report["error"]),
        )
    return old_res


def _extract_cores(
    old_res: CallResult, new_res: CallResult
) -> tuple[JsonValue | None, JsonValue | None, JsonValue | None]:
    old_core = extract_old_compare_core(old_res.body) if old_res.ok and old_res.body is not None else None
    if new_res.ok and new_res.body is not None:
        new_core, new_info = extract_new_compare_and_info(new_res.body)
    else:
        new_core, new_info = None, None
    return old_core, new_core, new_info


def _pick_old_values(old_core: JsonValue | None, key: str) -> tuple[JsonValue | None, JsonValue | None]:
    if isinstance(old_core, dict) and isinstance(old_core.get(key), dict):
        entry = old_core[key]
        return entry.get("predicted_answer"), entry.get("qa_status")
    return None, None


def _pick_new_values(new_core: JsonValue | None, key: str) -> tuple[JsonValue | None, JsonValue | None]:
    if isinstance(new_core, dict) and isinstance(new_core.get(key), dict):
        entry = new_core[key]
        return entry.get("predicted_answer"), entry.get("qa_status")
    return None, None


def _attach_debug_json(
    rows: list[dict[str, JsonValue]],
    old_core: JsonValue | None,
    new_core: JsonValue | None,
    new_info: JsonValue | None,
) -> None:
    if not rows:
        return

    rows[0]["old_core_json"] = json.dumps(old_core, ensure_ascii=False, sort_keys=True, indent=2) if old_core else None
    rows[0]["new_core_json"] = json.dumps(new_core, ensure_ascii=False, sort_keys=True, indent=2) if new_core else None
    rows[0]["new_previous_answers_json"] = (
        json.dumps(new_info, ensure_ascii=False, sort_keys=True, indent=2) if new_info else None
    )


def strip_volatile(x: JsonValue) -> JsonValue:
    """Recursively remove volatile keys from nested JSON-like structures."""
    if isinstance(x, dict):
        return {k: strip_volatile(v) for k, v in x.items() if k not in VOLATILE_KEYS}
    if isinstance(x, list):
        return [strip_volatile(v) for v in x]
    return x


def _json_cell(x: JsonValue) -> JsonValue:
    """Excel-friendly cell representation (JSON string for lists/dicts)."""
    if isinstance(x, (dict, list)):
        return json.dumps(x, ensure_ascii=False, sort_keys=True)
    return x


def _norm_answer(x: JsonValue) -> JsonValue:
    """Normalize simple answers so comparisons aren't too brittle."""
    if isinstance(x, str):
        s = x.strip()
        low = s.lower()
        if low in {"yes", "y", "true"}:
            return "Yes"
        if low in {"no", "n", "false"}:
            return "No"
        return s
    if isinstance(x, bool):
        return "Yes" if x else "No"
    return x


def _answers_equal(pred: JsonValue, truth: JsonValue) -> bool:
    return _norm_answer(pred) == _norm_answer(truth)


def _qa_status_to_hit(status: JsonValue) -> bool | None:
    """Map OLD qa_status/verdict to hit/miss."""
    if status is None or not isinstance(status, str):
        return None

    s = status.strip()
    s = s.split(".")[-1].strip().lower()

    if s in {"qaaccepted", "accepted"}:
        return True
    if s in {"qarejected", "rejected"}:
        return False
    return None


async def _call_both_flows(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    cfg: Config,
    data_id: str,
) -> tuple[CallResult, CallResult]:
    old_url = f"{cfg.base_url}{cfg.old_path_tmpl.format(data_id=data_id)}"
    new_url = f"{cfg.base_url}{cfg.new_path_tmpl.format(data_id=data_id)}"
    old_payload, new_payload = _build_payloads(cfg)

    async with sem:
        old_res = await post_json(client, old_url, old_payload)
    async with sem:
        new_res = await post_json(client, new_url, new_payload)

    return _patch_old_error(old_res), new_res


@dataclass(frozen=True)
class RowContext:
    """Context for building per-datapoint comparison rows."""

    dataset_id: str
    old_res: CallResult
    new_res: CallResult
    old_core: JsonValue | None
    new_core: JsonValue | None
    new_info: JsonValue | None


def _make_datapoint_rows(ctx: RowContext) -> list[dict[str, JsonValue]]:
    truth = _extract_truth_from_new_info(ctx.new_info)
    keys = sorted(truth.keys())
    rows: list[dict[str, JsonValue]] = []
    for key in keys:
        t = truth.get(key)
        has_truth = t is not None
        o_pred, o_status = _pick_old_values(ctx.old_core, key)
        n_pred, n_status = _pick_new_values(ctx.new_core, key)
        old_hits = _qa_status_to_hit(o_status) if has_truth else None
        new_hits = _answers_equal(n_pred, t) if has_truth else None

        rows.append(
            {
                "dataset_id": ctx.dataset_id,
                "datapoint_key": key,
                "dataland_previous_answer": _json_cell(t),
                "old_predicted": _json_cell(o_pred),
                "new_predicted": _json_cell(n_pred),
                "old_qa_status": o_status,
                "new_qa_status": n_status,
                "has_truth": has_truth,
                "old_hits_dataland": old_hits,
                "new_hits_dataland": new_hits,
                "old_ok": ctx.old_res.ok,
                "new_ok": ctx.new_res.ok,
                "old_status": ctx.old_res.status_code,
                "new_status": ctx.new_res.status_code,
                "old_latency_ms": ctx.old_res.latency_ms,
                "new_latency_ms": ctx.new_res.latency_ms,
                "old_error": ctx.old_res.error,
                "new_error": ctx.new_res.error,
            }
        )

    _attach_debug_json(rows, ctx.old_core, ctx.new_core, ctx.new_info)
    return rows


@dataclass
class CallResult:
    """HTTP call result for one endpoint invocation."""

    ok: bool
    status_code: int | None
    latency_ms: int | None
    body: JsonValue | None
    error: str | None


async def post_json(client: httpx.AsyncClient, url: str, payload: dict[str, JsonValue]) -> CallResult:
    """POST JSON payload to an endpoint and capture status, latency, and response body."""
    start = time.perf_counter()
    try:
        r = await client.post(url, json=payload)
        latency_ms = int((time.perf_counter() - start) * 1000)

        ct = r.headers.get("content-type") or ""
        body: JsonValue = r.json() if "application/json" in ct else {"raw_text": r.text}

        ok = HTTP_OK_MIN <= r.status_code < HTTP_OK_MAX
        error = None if ok else f"HTTP {r.status_code}"
        return CallResult(ok=ok, status_code=r.status_code, latency_ms=latency_ms, body=body, error=error)
    except Exception as e:  # noqa: BLE001
        latency_ms = int((time.perf_counter() - start) * 1000)
        return CallResult(ok=False, status_code=None, latency_ms=latency_ms, body=None, error=str(e))


@dataclass(frozen=True)
class Config:
    """Runtime configuration for the n&g flow comparison script."""

    base_url: str
    ids_file: str
    out: str
    ai_model: str
    use_ocr: bool
    force_review: bool
    override: bool
    timeout: float
    concurrency: int
    old_path_tmpl: str
    new_path_tmpl: str


def parse_args() -> Config:
    """Parse CLI args and environment variables into a Config object."""
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default=os.getenv("NG_BASE_URL", "http://127.0.0.1:64631"),
        help="Base URL of the API server.",
    )
    parser.add_argument(
        "--ids-file",
        required=True,
        help="Text file containing one dataset_id per line.",
    )
    parser.add_argument(
        "--out",
        default="ng_compare.xlsx",
        help="Output Excel file path.",
    )
    parser.add_argument(
        "--ai-model",
        default=os.getenv("NG_AI_MODEL", "gpt-5"),
        help="AI model name passed to both flows.",
    )
    parser.add_argument(
        "--use-ocr",
        action="store_true",
        default=os.getenv("NG_USE_OCR", "true").lower() == "true",
        help="Enable OCR during review.",
    )
    parser.add_argument(
        "--force-review",
        action="store_true",
        default=os.getenv("NG_FORCE_REVIEW", "true").lower() == "true",
        help="Force review even if already reviewed (old flow).",
    )
    parser.add_argument(
        "--override",
        action="store_true",
        default=os.getenv("NG_OVERRIDE", "true").lower() == "true",
        help="Override the new flow's review decision (forces revalidation).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("NG_TIMEOUT_SECONDS", "300")),
        help="HTTP timeout in seconds.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=int(os.getenv("NG_CONCURRENCY", "1")),
        help="Number of concurrent requests (keep low for dev).",
    )

    parser.add_argument(
        "--old-path",
        default=os.getenv("NG_OLD_PATH", "/review/{data_id}"),
        help="Old endpoint path template.",
    )
    parser.add_argument(
        "--new-path",
        default=os.getenv("NG_NEW_PATH", "/data-point-flow/review-dataset/{data_id}"),
        help="New endpoint path template.",
    )

    args = parser.parse_args()

    return Config(
        base_url=args.base_url.rstrip("/"),
        ids_file=args.ids_file,
        out=args.out,
        ai_model=args.ai_model,
        use_ocr=bool(args.use_ocr),
        force_review=bool(args.force_review),
        override=bool(args.override),
        timeout=args.timeout,
        concurrency=args.concurrency,
        old_path_tmpl=args.old_path,
        new_path_tmpl=args.new_path,
    )


def read_dataset_ids(path: str) -> list[str]:
    """Read dataset IDs from a newline-delimited text file."""
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def _get_path(d: JsonValue, *path: str) -> JsonValue:
    cur: JsonValue = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def _canonicalize_new_key(k: str) -> str:
    """Canonicalize NEW datapoint type names to match OLD report keys."""
    ck = k

    ck2 = ck.removeprefix("extendedEnumYesNo")
    if ck2 != ck:
        return ck2[:1].lower() + ck2[1:] if ck2 else ck

    if ck.startswith("extendedNuclearAndGas") and "Component" in ck:
        left, right = ck.split("Component", 1)

        group = left.removeprefix("extendedNuclearAndGas")
        group_map = {
            "AlignedDenominator": "taxonomyAlignedDenominator",
            "AlignedNumerator": "taxonomyAlignedNumerator",
            "EligibleButNotAligned": "taxonomyEligibleButNotAligned",
            "NonEligible": "taxonomyNonEligible",
        }
        group_key = group_map.get(group)
        if group_key:
            field = right[:1].lower() + right[1:] if right else right
            return f"{group_key}.{field}"

    return ck


def _extract_old_predicted_from_corrected(entry: dict[str, JsonValue]) -> JsonValue:
    corrected = entry.get("correctedData")
    if not isinstance(corrected, dict):
        return None

    val = corrected.get("value")
    if isinstance(val, (str, int, float, bool)) or val is None or isinstance(val, (dict, list)):
        return val

    if isinstance(val, dict) and "value" in val:
        inner = val.get("value")
        if isinstance(inner, (str, int, float, bool)) or inner is None or isinstance(inner, (dict, list)):
            return inner

    return None


def extract_old_compare_core(body: JsonValue) -> dict[str, dict[str, JsonValue]] | None:
    """Normalize OLD response into a comparable dict keyed like the OLD report."""
    general = _get_path(body, "data", "report", "general")
    if not isinstance(general, dict):
        return None

    out: dict[str, dict[str, JsonValue]] = {}

    gen_gen = general.get("general")
    if isinstance(gen_gen, dict):
        for k, v in gen_gen.items():
            if not isinstance(v, dict):
                continue
            out[k] = {
                "qa_status": v.get("verdict"),
                "predicted_answer": _extract_old_predicted_from_corrected(v),
            }

    for group_name, group_val in general.items():
        if group_name == "general":
            continue
        if not isinstance(group_val, dict):
            continue
        for k, v in group_val.items():
            if not isinstance(v, dict):
                continue
            out[f"{group_name}.{k}"] = {
                "qa_status": v.get("verdict"),
                "predicted_answer": _extract_old_predicted_from_corrected(v),
            }

    return out


def extract_new_compare_and_info(
    body: JsonValue,
) -> tuple[dict[str, dict[str, JsonValue]] | None, dict[str, dict[str, JsonValue]] | None]:
    """Normalize NEW response into a comparable dict (like OLD report) plus an info dict for additional context."""
    if not isinstance(body, dict):
        return None, None

    compare: dict[str, dict[str, JsonValue]] = {}
    info: dict[str, dict[str, JsonValue]] = {}

    for k, v in body.items():
        if not isinstance(v, dict):
            continue

        ck = _canonicalize_new_key(k)

        compare[ck] = {
            "qa_status": v.get("qa_status"),
            "predicted_answer": v.get("predicted_answer"),
        }
        info[ck] = {
            "previous_answer": v.get("previous_answer"),
        }

    return compare, info


def _extract_truth_from_new_info(new_info: dict[str, dict[str, JsonValue]] | None) -> dict[str, JsonValue]:
    truth: dict[str, JsonValue] = {}
    if not isinstance(new_info, dict):
        return truth
    for k, v in new_info.items():
        if isinstance(v, dict):
            truth[k] = v.get("previous_answer")
    return truth


async def run_comparison(cfg: Config, dataset_ids: list[str]) -> list[dict[str, JsonValue]]:
    """Compare old vs. new flow against Dataland previous_answer and return report rows."""
    headers = _auth_headers()

    limits = httpx.Limits(
        max_connections=cfg.concurrency,
        max_keepalive_connections=cfg.concurrency,
    )
    sem = asyncio.Semaphore(cfg.concurrency)

    async with httpx.AsyncClient(headers=headers, timeout=cfg.timeout, limits=limits) as client:

        async def run_one(data_id: str) -> list[dict[str, JsonValue]]:
            old_res, new_res = await _call_both_flows(client, sem, cfg, data_id)

            old_core, new_core, new_info = _extract_cores(old_res, new_res)

            ctx = RowContext(
                dataset_id=data_id,
                old_res=old_res,
                new_res=new_res,
                old_core=old_core,
                new_core=new_core,
                new_info=new_info,
            )
            return _make_datapoint_rows(ctx)

        nested = await asyncio.gather(*(run_one(i) for i in dataset_ids))
        return [row for rows in nested for row in rows]


def _to_bool_or_na(s: pd.Series) -> pd.Series:
    return s.map(lambda x: pd.NA if x is None else bool(x)).astype("boolean")


def write_report(rows: list[dict[str, JsonValue]], out_path: str) -> None:
    """Write summary + per-datapoint results + pivots to an Excel file."""
    df = pd.DataFrame(rows)

    for col in ["old_ok", "new_ok"]:
        if col in df.columns:
            df[col] = df[col].fillna(False).infer_objects(copy=False).astype(bool)

    for col in ["old_hits_dataland", "new_hits_dataland"]:
        if col in df.columns:
            df[col] = _to_bool_or_na(df[col])

    def _hit_rate(series: pd.Series) -> float | None:
        s = series.dropna()
        if len(s) == 0:
            return None
        return float(s.mean())

    grouped = df.groupby("dataset_id", dropna=False)

    ds_summary = grouped.agg(
        truth_count=("has_truth", lambda s: int(s.fillna(False).sum())),
        old_hit_rate=("old_hits_dataland", _hit_rate),
        new_hit_rate=("new_hits_dataland", _hit_rate),
        old_hits=("old_hits_dataland", lambda s: int(s.dropna().sum()) if len(s.dropna()) else 0),
        new_hits=("new_hits_dataland", lambda s: int(s.dropna().sum()) if len(s.dropna()) else 0),
        old_missing=("old_predicted", lambda s: int(pd.isna(s).sum())),
        new_missing=("new_predicted", lambda s: int(pd.isna(s).sum())),
        old_ok=("old_ok", "min"),
        new_ok=("new_ok", "min"),
        old_status=("old_status", "max"),
        new_status=("new_status", "max"),
        old_latency_ms=("old_latency_ms", "max"),
        new_latency_ms=("new_latency_ms", "max"),
    ).reset_index()

    int_cols = [
        "truth_count",
        "old_hits",
        "new_hits",
        "old_missing",
        "new_missing",
        "old_status",
        "new_status",
        "old_latency_ms",
        "new_latency_ms",
    ]
    float_cols = ["old_hit_rate", "new_hit_rate"]

    for c in int_cols:
        if c in ds_summary.columns:
            ds_summary[c] = pd.to_numeric(ds_summary[c], errors="coerce").astype("Int64")

    for c in float_cols:
        if c in ds_summary.columns:
            ds_summary[c] = pd.to_numeric(ds_summary[c], errors="coerce").astype("float64")

    overall = pd.DataFrame(
        [
            {
                "datasets": int(ds_summary["dataset_id"].nunique()) if len(ds_summary) else 0,
                "rows_datapoints": len(df),
                "old_fail_datasets": int((~ds_summary["old_ok"]).sum()) if len(ds_summary) else 0,
                "new_fail_datasets": int((~ds_summary["new_ok"]).sum()) if len(ds_summary) else 0,
                "avg_old_latency_ms": float(ds_summary["old_latency_ms"].dropna().mean()) if len(ds_summary) else None,
                "avg_new_latency_ms": float(ds_summary["new_latency_ms"].dropna().mean()) if len(ds_summary) else None,
                "avg_old_hit_rate": float(ds_summary["old_hit_rate"].dropna().mean()) if len(ds_summary) else None,
                "avg_new_hit_rate": float(ds_summary["new_hit_rate"].dropna().mean()) if len(ds_summary) else None,
            }
        ]
    )

    pivot = (
        df.groupby("datapoint_key", dropna=False)
        .agg(
            count=("dataset_id", "count"),
            truth_count=("old_hits_dataland", lambda s: int(s.dropna().shape[0])),
            old_hit_rate=("old_hits_dataland", _hit_rate),
            new_hit_rate=("new_hits_dataland", _hit_rate),
        )
        .reset_index()
        .sort_values(by=["truth_count", "datapoint_key"], ascending=[False, True])
    )

    for c in ["count", "truth_count"]:
        if c in pivot.columns:
            pivot[c] = pd.to_numeric(pivot[c], errors="coerce").astype("Int64")

    for c in ["old_hit_rate", "new_hit_rate"]:
        if c in pivot.columns:
            pivot[c] = pd.to_numeric(pivot[c], errors="coerce").astype("float64")

    mismatches = df[
        (df["old_hits_dataland"].notna() & (df["old_hits_dataland"].eq(False)))
        | (df["new_hits_dataland"].notna() & (df["new_hits_dataland"].eq(False)))
    ].copy()

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        overall.to_excel(writer, index=False, sheet_name="summary_overall")
        ds_summary.to_excel(writer, index=False, sheet_name="summary_by_dataset")
        df.to_excel(writer, index=False, sheet_name="results_by_datapoint")
        pivot.to_excel(writer, index=False, sheet_name="pivot_by_datapoint_key")
        mismatches.to_excel(writer, index=False, sheet_name="mismatches_vs_dataland")


async def main() -> int:
    """Entry point: parse config, run comparison, and write the Excel report."""
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    cfg = parse_args()
    dataset_ids = read_dataset_ids(cfg.ids_file)

    rows = await run_comparison(cfg, dataset_ids)
    write_report(rows, cfg.out)

    logger.info("Wrote %s (%s datapoint rows)", cfg.out, len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
