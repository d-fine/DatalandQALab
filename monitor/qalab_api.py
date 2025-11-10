import sys
from urllib.parse import urljoin

import requests

from monitor.utils import load_config

config = load_config()


def check_qalab_api_health() -> None:
    """Check if the QALab API is healthy."""
    url = urljoin(config.qa_lab_url, "/health")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        sys.exit(1)


def run_report_on_qalab(data_id: str, ai_model: str, use_ocr: bool) -> dict:
    """Get data from Dataland QA Lab for monitoring purposes."""
    url = urljoin(config.qa_lab_url, f"/review/{data_id}")
    params = {"ai_model": ai_model, "use_ocr": use_ocr, "force_review": False}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
