import json
import logging
import os
import pathlib
import time
from collections import Counter
from dataclasses import dataclass, field

base_dir = pathlib.Path(__file__).parent
output_dir = base_dir / "output"
config_path = base_dir / "config.json"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


@dataclass
class MonitorConfig:
    """Configuration class for the monitor."""

    documents: list[str] = field(default_factory=list)
    qa_lab_url: str = "http://localhost:8000"
    ai_model: str = "gpt-4"
    use_ocr: bool = False
    force_review: bool = False
    use_datapoint_endpoint: bool = False


def load_config() -> MonitorConfig:
    """Load configuration from a JSON file or environment variables (if no json is found)."""
    try:
        with pathlib.Path(config_path).open(encoding="utf-8") as f:
            config = json.load(f)
            return MonitorConfig(
                qa_lab_url=config.get("qa_lab_url", "http://localhost:8000"),
                documents=config.get("documents", []),
                ai_model=config.get("ai_model", "gpt-4"),
                use_ocr=config.get("use_ocr", False),
                force_review=config.get("force_review", False),
                use_datapoint_endpoint=config.get("use_datapoint_endpoint", False),
            )
    except (json.JSONDecodeError, OSError):
        logger.warning("Config file not found or invalid, falling back to environment variables.")

    qa_lab_url = os.getenv("QA_LAB_URL", "http://localhost:8000")
    documents_env = os.getenv("DOCUMENTS", "")
    documents = documents_env.split(",") if documents_env else []
    ai_model = os.getenv("AI_MODEL", "gpt-4")
    use_ocr = os.getenv("USE_OCR", "0").strip().lower() in {"1", "true", "yes"}
    force_review = os.getenv("FORCE_REVIEW", "0").strip().lower() in {"1", "true", "yes"}
    use_datapint_endpoint = os.getenv("USE_DATAPOINT_ENDPOINT", "0").strip().lower() in {"1", "true", "yes"}

    return MonitorConfig(
        qa_lab_url=qa_lab_url,
        documents=documents,
        ai_model=ai_model,
        use_ocr=use_ocr,
        force_review=force_review,
        use_datapoint_endpoint=use_datapint_endpoint,
    )


def store_output(data: str | list | dict, file_name: str, timestamp: bool = True, format_as_json: bool = False) -> None:
    """Store output data to a file in the output directory (which gets stored as an artifact later on)."""
    pathlib.Path(output_dir).mkdir(exist_ok=True, parents=True)
    timestamp_value = int(time.time()) if timestamp else ""
    with pathlib.Path(f"{output_dir}/{file_name}-{timestamp_value}.json").open("w", encoding="utf-8") as f:
        if format_as_json:
            json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            f.write(str(data))


def match_sot_and_qareport(source_of_truth: dict, qalab_report: dict) -> dict:
    """Compare source of truth with QALab report to check for consistency."""
    fields = {
        key
        for key in source_of_truth.get("data", {}).get("general", {}).get("general", {})
        if key != "referenced_reports"
    }
    qa_general = qalab_report.get("data", {}).get("report", {}).get("general", {}).get("general", {})

    counter = Counter()

    for report_field in fields:
        qa_field = snake_case_to_camel_case(report_field)
        verdict = qa_general.get(qa_field, {}).get("verdict")
        counter[verdict] += 1

    return {
        "total_fields": len(fields),
        "qa_accepted": counter["QaAccepted"],
        "qa_rejected": counter["QaRejected"],
        "qa_inconclusive": counter["QaInconclusive"],
        "qa_not_attempted": counter["QaNotAttempted"],
    }


def snake_case_to_camel_case(snake_str: str) -> str:
    """Convert snake_case string to camelCase."""
    first, *rest = snake_str.split("_")
    return first + "".join(word.title() for word in rest)
