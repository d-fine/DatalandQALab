import datetime
import json
import logging
import os
import pathlib
import sys
from dataclasses import dataclass, field

base_dir = pathlib.Path(__file__).parent
output_dir = base_dir / "output"
config_path = base_dir / "config.json"

cet_timezone = datetime.timezone(datetime.timedelta(hours=1))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


@dataclass
class MonitorConfig:
    """Configuration class for the monitor."""

    documents: list[str] = field(default_factory=list)
    qa_lab_url: str = "http://localhost:8000"
    ai_model: str = "gpt-4"


def load_config() -> MonitorConfig:
    """Load configuration from a JSON file or environment variables (if no json is found)."""
    try:
        with pathlib.Path(config_path).open(encoding="utf-8") as f:
            config = json.load(f)
            return MonitorConfig(
                qa_lab_url=config.get("qa_lab_url", "http://localhost:8000"),
                documents=config.get("documents", []),
                ai_model=config.get("ai_model", "gpt-4"),
            )
    except (json.JSONDecodeError, OSError):
        logger.warning("Config file not found or invalid, falling back to environment variables.")

    qa_lab_url = os.getenv("QA_LAB_URL", "http://localhost:8000")
    documents_env = os.getenv("DOCUMENTS", "")
    documents = documents_env.split(",") if documents_env else []
    ai_model = os.getenv("AI_MODEL", "gpt-4")

    return MonitorConfig(
        qa_lab_url=qa_lab_url,
        documents=documents,
        ai_model=ai_model,
    )


def store_output(data: str, file_name: str, format_as_json: bool = False) -> None:
    """Store output data to a file in the output directory (which gets stored as an artifact later on)."""
    pathlib.Path(output_dir).mkdir(exist_ok=True, parents=True)
    with pathlib.Path(f"{output_dir}/{file_name}-{datetime.datetime.now(tz=cet_timezone)}").open(
        "w", encoding="utf-8"
    ) as f:
        if format_as_json:
            json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            f.write(data)
