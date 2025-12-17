"""Validate a list of datapoint IDs and save results.

Usage:
  pdm run python scripts/validate_datapoints.py --input datapoints.csv --out results.json

The input CSV should contain a header with columns: data_point_id, company_id (company_id optional).
This script will call dataland_qa_lab.review.dataset_reviewer.validate_datapoint for each id.

CAUTION: This performs real validation calls (may call AI, OCR and Dataland APIs). Run against staging when possible.
"""

import argparse
import csv
import json
import logging
import time
from pathlib import Path

try:
    import pandas as pd  # optional, required for Excel support
except ImportError:
    pd = None

from dataland_qa_lab.review import dataset_reviewer
from dataland_qa_lab.utils import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_list(
    data_point_ids: list[str], ai_model: str | None = None, use_ocr: bool = True
) -> list[dict]:
    """Validate datapoint IDs and return result dictionaries."""
    cfg = config.get_config()
    results: list[dict] = []
    for dp in data_point_ids:
        logger.info("Validating data point %s", dp)
        # Pre-check: fetch datapoint and ensure it has a dataSource and a prompt
        try:
            data_point = cfg.dataland_client.data_points_api.get_data_point(dp)
            dp_json = json.loads(data_point.data_point)
        except Exception as exc:  # pragma: no cover - passthrough of client errors
            logger.exception("Failed to fetch data point %s", dp)
            results.append({"data_point_id": dp, "error": f"Failed to fetch datapoint: {exc}"})
            time.sleep(1)
            continue

        if dp_json.get("dataSource") is None:
            msg = "missing dataSource"
            logger.warning("Skipping %s: %s", dp, msg)
            results.append({"data_point_id": dp, "error": msg})
            time.sleep(1)
            continue

        data_point_type = getattr(data_point, "data_point_type", None) or dp_json.get("dataPointType")
        # Use the in-memory prompts from dataset_reviewer so we avoid expensive OCR/AI when not possible
        prompt_template = dataset_reviewer.validation_prompts.get(data_point_type, {}).get("prompt")
        if prompt_template is None:
            msg = f"no prompt for data point type: {data_point_type}"
            logger.warning("Skipping %s: %s", dp, msg)
            results.append({"data_point_id": dp, "error": msg})
            time.sleep(1)
            continue

        try:
            res = dataset_reviewer.validate_datapoint(
                data_point_id=dp, ai_model=ai_model or cfg.ai_model, use_ocr=use_ocr, override=False
            )
            results.append(
                {
                    "data_point_id": res.data_point_id,
                    "data_point_type": res.data_point_type,
                    "previous_answer": res.previous_answer,
                    "predicted_answer": res.predicted_answer,
                    "qa_status": str(res.qa_status),
                    "confidence": getattr(res, "confidence", None),
                    "reasoning": getattr(res, "reasoning", None),
                    "timestamp": res.timestamp,
                }
            )
        except Exception as exc:  # pragma: no cover - passthrough of client errors
            logger.exception("Validation failed for %s", dp)
            results.append({"data_point_id": dp, "error": str(exc)})
        # small delay to avoid overloading services
        time.sleep(1)
    return results


def read_csv(input_path: str) -> list[str]:
    """Read data_point_id values from a CSV file."""
    with Path(input_path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row["data_point_id"].strip() for row in reader if row.get("data_point_id", "").strip()]


def read_excel(input_path: str) -> list[str]:
    """Read data_point_id values from an Excel file."""
    if pd is None:
        message = (
            "pandas is required to read Excel files. Install it with 'pdm add pandas openpyxl' "
            "or run the script with a CSV input."
        )
        raise RuntimeError(message)
    df = pd.read_excel(input_path, engine="openpyxl")
    if "data_point_id" in df.columns:
        ids = [str(val).strip() for val in df["data_point_id"].dropna()]
    else:
        message = "Excel file must contain a 'data_point_id' column"
        raise RuntimeError(message)
    return ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input CSV with data_point_id column")
    parser.add_argument("--out", required=False, default="validate_results.json", help="Output JSON file")
    parser.add_argument(
        "--limit", required=False, type=int, default=0, help="Limit number of datapoints to validate (0 = no limit)"
    )
    parser.add_argument("--ai_model", required=False, help="AI model to use (overrides config)")
    parser.add_argument("--use_ocr", required=False, default="true", help="use OCR: true|false")
    args = parser.parse_args()

    use_ocr_flag = str(args.use_ocr).lower() in {"1", "true", "yes", "y"}

    input_path = args.input
    p = Path(input_path)
    dps = read_excel(input_path) if p.suffix.lower() in {".xlsx", ".xls"} else read_csv(input_path)

    if args.limit and args.limit > 0:
        dps = dps[: args.limit]
    logger.info("Loaded %d data_point_ids from %s", len(dps), args.input)

    results = validate_list(dps, ai_model=args.ai_model, use_ocr=use_ocr_flag)

    with Path(args.out).open("w", encoding="utf-8") as out_f:
        json.dump(results, out_f, indent=2, ensure_ascii=False)

    logger.info("Saved results to %s", args.out)
