import requests


def review_data_point(data_point_id: str, ai_model: str, use_ocr: bool) -> dict:
    """Trigger monitoring for a specific data point via an API call."""
    api_url = f"http://127.0.0.1:8000/data-point-flow/review-data-point/{data_point_id}"
    payload = {
        "ai_model": ai_model,
        "use_ocr": use_ocr,
    }
    response = requests.post(api_url, json=payload)
    return response.json()


def review_dataset(dataset_id: str, ai_model: str, use_ocr: bool) -> dict:
    """Trigger monitoring for a specific dataset via an API call."""
    api_url = f"http://127.0.0.1:8000/data-point-flow/review-dataset/{dataset_id}"
    payload = {
        "ai_model": ai_model,
        "use_ocr": use_ocr,
    }
    response = requests.post(api_url, json=payload)
    return response.json()
