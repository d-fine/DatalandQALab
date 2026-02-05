from __future__ import annotations

import argparse
import asyncio
import hashlib
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


def strip_volatile(x: JsonValue) -> JsonValue:
    """Recursively remove volatile keys from nested JSON-like structures."""
    if isinstance(x, dict):
        return {k: strip_volatile(v) for k, v in x.items() if k not in VOLATILE_KEYS}
    if isinstance(x, list):
        return [strip_volatile(v) for v in x]
    return x


def stable_hash(x: JsonValue) -> str:
    """Compute a deterministic hash of a JSON-like structure."""
    cleaned = strip_volatile(x)
    s = json.dumps(cleaned, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


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
        body = r.json() if "application/json" in ct else {"raw_text": r.text}

        ok = HTTP_OK_MIN <= r.status_code < HTTP_OK_MAX
        error = None if ok else f"HTTP {r.status_code}"
        return CallResult(
            ok=ok,
            status_code=r.status_code,
            latency_ms=latency_ms,
            body=body,
            error=error,
        )
    except Exception as e:  # noqa: BLE001
        latency_ms = int((time.perf_counter() - start) * 1000)
        return CallResult(ok=False, status_code=None, latency_ms=latency_ms, body=None, error=str(e))


def top_level_diff(a: JsonValue, b: JsonValue) -> str | None:
    """Create a small human-readable diff hint for top-level dict key mismatches."""
    if isinstance(a, dict) and isinstance(b, dict):
        ak, bk = set(a.keys()), set(b.keys())
        only_b = sorted(bk - ak)[:10]
        only_a = sorted(ak - bk)[:10]
        if only_a or only_b:
            return f"top-level keys differ: only_old={only_a} only_new={only_b}"
    return None


@dataclass(frozen=True)
class Config:
    """Runtime configuration for the n&g flow comparison script."""

    base_url: str
    ids_file: str
    out: str
    ai_model: str
    use_ocr: bool
    force_review: bool
    override_obj: JsonValue | None
    timeout: float
    concurrency: int


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
        default=os.getenv("NG_FORCE_REVIEW", "false").lower() == "true",
        help="Force review even if already reviewed (old flow).",
    )
    parser.add_argument(
        "--override-json",
        default=os.getenv("NG_OVERRIDE_JSON", ""),
        help="JSON string for the new flow 'override' field (optional).",
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

    args = parser.parse_args()
    override_obj = json.loads(args.override_json) if args.override_json.strip() else None

    return Config(
        base_url=args.base_url.rstrip("/"),
        ids_file=args.ids_file,
        out=args.out,
        ai_model=args.ai_model,
        use_ocr=bool(args.use_ocr),
        force_review=bool(args.force_review),
        override_obj=override_obj,
        timeout=args.timeout,
        concurrency=args.concurrency,
    )


def read_dataset_ids(path: str) -> list[str]:
    """Read dataset IDs from a newline-delimited text file."""
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_report(rows: list[dict[str, JsonValue]], out_path: str) -> None:
    """Write summary and row-level results to an Excel file."""
    df = pd.DataFrame(rows)
    summary = pd.DataFrame(
        [
            {
                "total": len(df),
                "matches": int(df["match"].sum()),
                "mismatches": int((~df["match"]).sum()),
                "old_failures": int((~df["old_ok"]).sum()),
                "new_failures": int((~df["new_ok"]).sum()),
                "avg_old_latency_ms": float(df["old_latency_ms"].dropna().mean()) if len(df) else None,
                "avg_new_latency_ms": float(df["new_latency_ms"].dropna().mean()) if len(df) else None,
            }
        ],
    )
    mismatches = df[df["match"] == False].copy()  # noqa: E712

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="summary")
        df.to_excel(writer, index=False, sheet_name="results")
        mismatches.to_excel(writer, index=False, sheet_name="mismatches")


async def run_comparison(cfg: Config, dataset_ids: list[str]) -> list[dict[str, JsonValue]]:
    """Call old and new endpoints for each dataset ID and return row dicts."""
    headers: dict[str, str] = {}
    token = os.getenv("NG_AUTH_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    limits = httpx.Limits(
        max_connections=cfg.concurrency,
        max_keepalive_connections=cfg.concurrency,
    )
    sem = asyncio.Semaphore(cfg.concurrency)

    old_path_tmpl = "/review/{data_id}"
    new_path_tmpl = "/data-point-flow/review-dataset/{data_id}"

    async with httpx.AsyncClient(headers=headers, timeout=cfg.timeout, limits=limits) as client:

        async def run_one(data_id: str) -> dict[str, JsonValue]:
            old_url = f"{cfg.base_url}{old_path_tmpl.format(data_id=data_id)}"
            new_url = f"{cfg.base_url}{new_path_tmpl.format(data_id=data_id)}"

            old_payload = {
                "force_review": cfg.force_review,
                "ai_model": cfg.ai_model,
                "use_ocr": cfg.use_ocr,
            }
            new_payload = {
                "ai_model": cfg.ai_model,
                "use_ocr": cfg.use_ocr,
                "override": cfg.override_obj,
            }

            async with sem:
                old_res = await post_json(client, old_url, old_payload)
            async with sem:
                new_res = await post_json(client, new_url, new_payload)

            old_core = (
                old_res.body.get("data") if isinstance(old_res.body, dict) and "data" in old_res.body else old_res.body
            )
            new_core = new_res.body

            old_hash = stable_hash(old_core) if old_res.ok else None
            new_hash = stable_hash(new_core) if new_res.ok else None

            match = bool(old_res.ok and new_res.ok and old_hash and new_hash and old_hash == new_hash)

            diff_summary = None
            if not match:
                if old_res.error or new_res.error:
                    diff_summary = f"old_error={old_res.error} | new_error={new_res.error}"
                else:
                    diff_summary = (
                        top_level_diff(strip_volatile(old_core), strip_volatile(new_core)) or "normalized hash mismatch"
                    )

            return {
                "dataset_id": data_id,
                "old_status": old_res.status_code,
                "old_ok": old_res.ok,
                "old_latency_ms": old_res.latency_ms,
                "old_hash": old_hash,
                "old_error": old_res.error,
                "new_status": new_res.status_code,
                "new_ok": new_res.ok,
                "new_latency_ms": new_res.latency_ms,
                "new_hash": new_hash,
                "new_error": new_res.error,
                "match": match,
                "diff_summary": diff_summary,
            }

        return await asyncio.gather(*(run_one(i) for i in dataset_ids))


async def main() -> int:
    """Entry point: parse config, run comparison, and write the Excel report."""
    cfg = parse_args()
    dataset_ids = read_dataset_ids(cfg.ids_file)
    rows = await run_comparison(cfg, dataset_ids)
    write_report(rows, cfg.out)
    logger.info("Wrote %s (%s rows)", cfg.out, len(rows))

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
