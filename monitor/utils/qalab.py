import requests


def is_healthy(qalab_base_url: str) -> bool:
    """Check the health of the QaLab service."""
    api_url = f"{qalab_base_url}/health"
    try:
        response = requests.request("GET", api_url)
    except requests.RequestException:
        return False
    else:
        return response.status_code == requests.codes.ok


def review_data_point(qalab_base_url: str, data_point_id: str, ai_model: str, use_ocr: bool, override: bool) -> dict:
    """Trigger monitoring for a specific data point via an API call."""
    api_url = f"{qalab_base_url}/data-point-flow/review-data-point/{data_point_id}"
    payload = {
        "ai_model": ai_model,
        "use_ocr": use_ocr,
        "override": override,
    }
    response = requests.post(api_url, json=payload)
    return response.json()


def review_dataset(qalab_base_url: str, dataset_id: str, ai_model: str, use_ocr: bool, override: bool) -> dict:
    """Trigger monitoring for a specific dataset via an API call."""
    api_url = f"{qalab_base_url}/data-point-flow/review-dataset/{dataset_id}"
    payload = {
        "ai_model": ai_model,
        "use_ocr": use_ocr,
        "override": override,
    }
    response = requests.post(api_url, json=payload)
    json_data = response.json()
    for k in json_data:
        json_data[k]["dataset_id"] = dataset_id

    return json_data
