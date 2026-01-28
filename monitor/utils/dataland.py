import os

import requests
from dotenv import load_dotenv

load_dotenv()
dataland_url = os.getenv("DATALAND_URL")
dataland_api_key = os.getenv("DATALAND_API_KEY")


def download_document(reference_id: str) -> any:
    """Download document by reference_id."""
    return requests.request(
        "GET",
        f"{dataland_url}/documents/{reference_id}",
        headers={"Authorization": f"Bearer {dataland_api_key}", "accept": "application/json"},
    )
