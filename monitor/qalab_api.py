import requests
import os
from urllib.parse import urljoin
from monitor.utils import load_config


config_path = os.path.join(os.path.dirname(__file__), "config.json")
config = load_config(config_path)
qalab_base_url = config.get("qa_lab_url", "http://127.0.0.1:8000")


def run_report_on_qalab(data_id: str, ai_model: str, use_ocr: bool) -> dict:
    """Get data from Dataland QA Lab for monitoring purposes."""
    url = urljoin(qalab_base_url, f"/review/{data_id}")
    params = {"ai_model": ai_model, "use_ocr": use_ocr, "force_review": False}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
