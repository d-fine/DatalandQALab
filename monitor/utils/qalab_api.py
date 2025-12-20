import logging
import sys
from urllib.parse import urljoin

import requests

from monitor.utils.utils import load_config

config = load_config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def check_qalab_api_health() -> None:
    """Check if the QALab API is healthy."""
    url = urljoin(config.qa_lab_url, "/health")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("QALab API health check failed. Please ensure the API is running and accessible.")
        sys.exit(1)


def run_report_on_qalab(data_id: str, ai_model: str, use_ocr: bool) -> dict:
    """Get data from Dataland QA Lab for monitoring purposes."""
    if config.use_datapoint_endpoint:
        url = urljoin(config.qa_lab_url, f"/data-point-flow/review-data-point/{data_id}")
        body = {"ai_model": ai_model, "use_ocr": use_ocr, "override": config.force_review}
    else:
        url = urljoin(config.qa_lab_url, f"/data-point-flow/review-dataset/{data_id}")
        body = {"ai_model": ai_model, "use_ocr": use_ocr, "force_review": config.force_review}

    response = requests.post(url, json=body, timeout=60 * 5)  # 5 minutes timeout since reviews can take time
    response.raise_for_status()
    return response.json()
