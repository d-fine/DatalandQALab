from typing import Final

import requests

REQUEST_TIMEOUT: Final[float] = 30.0


def _normalize_base_url(qalab_base_url: str) -> str:
    return qalab_base_url.rstrip("/")


def is_healthy(qalab_base_url: str) -> bool:
    """Check the health of the QaLab service."""
    api_url = f"{_normalize_base_url(qalab_base_url)}/health"
    try:
        response = requests.get(api_url, timeout=REQUEST_TIMEOUT)
    except requests.RequestException:
        return False
    return response.status_code == requests.codes.ok


def review_data_point(qalab_base_url: str, data_point_id: str, ai_model: str, use_ocr: bool, override: bool) -> dict:
    """Trigger monitoring for a specific data point via an API call."""
    api_url = f"{_normalize_base_url(qalab_base_url)}/data-point-flow/review-data-point/{data_point_id}"
    payload = {
        "ai_model": ai_model,
        "use_ocr": use_ocr,
        "override": override,
    }
    response = requests.post(api_url, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def review_dataset(qalab_base_url: str, dataset_id: str, ai_model: str, use_ocr: bool, override: bool) -> dict:
    """Trigger monitoring for a specific dataset via an API call."""
    api_url = f"{_normalize_base_url(qalab_base_url)}/data-point-flow/review-dataset/{dataset_id}"
    payload = {
        "ai_model": ai_model,
        "use_ocr": use_ocr,
        "override": override,
    }
    response = requests.post(api_url, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    json_data = response.json()
    for key in json_data:
        json_data[key]["dataset_id"] = dataset_id
    return json_data
