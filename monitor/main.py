import json
import logging
from typing import Any

import requests

from monitor.config import config
from monitor.utils import store_output, get_dataset_by_id

logger = logging.getLogger(__name__)


def check_qalab_api_health() -> None:
    """Check if the QALab API is reachable."""
    try:
        response = requests.get(f"{config.qalab_api_base_url}/health")
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        logger.error("QALab API health check failed: %s", exc)
        raise


def run_report_on_qalab(
    data_id: str,
    ai_model: str,
    use_ocr: bool,
    framework: str | None = None,
) -> dict[str, Any]:
    """Send document information to QALab API and return the JSON result."""

    payload: dict[str, Any] = {
        "document_id": data_id,
        "ai_model": ai_model,
        "use_ocr": use_ocr,
    }

    # Only include framework if provided (keeps tests happy)
    if framework is not None:
        payload["framework"] = framework

    logger.debug("Sending payload to QALab: %s", payload)

    response = requests.post(
        f"{config.qalab_api_base_url}/run-report",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def monitor_documents(
    documents: list[str],
    ai_model: str,
    use_ocr: bool = False,
    framework: str | None = None,
) -> None:
    """Retrieve a dataset, call QALab API, store output."""

    for doc_id in documents:
        logger.info("Processing document ID: %s", doc_id)

        dataset = get_dataset_by_id(doc_id)
        if dataset is None:
            logger.warning("Dataset %s not found; skipping", doc_id)
            continue

        try:
            raw_json = dataset.model_dump_json()
            data_dict = json.loads(raw_json)
        except Exception:  # noqa: BLE001
            logger.error("Invalid JSON for dataset %s; skipping", doc_id)
            continue

        result = run_report_on_qalab(
            data_id=doc_id,
            ai_model=ai_model,
            use_ocr=use_ocr,
            framework=framework,
        )

        store_output(doc_id, result)


def main() -> None:
    """Entry point for the monitoring tool."""

    check_qalab_api_health()

    # Build kwargs dynamically so tests don't fail due to unexpected arguments
    kwargs: dict[str, Any] = {
        "documents": config.documents,
        "ai_model": config.ai_model,
    }

    if getattr(config, "use_ocr", False):
        kwargs["use_ocr"] = config.use_ocr

    if getattr(config, "framework", None) is not None:
        kwargs["framework"] = config.framework

    monitor_documents(**kwargs)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
