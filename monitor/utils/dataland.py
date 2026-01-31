import os
from typing import Final

import requests
from dotenv import load_dotenv

load_dotenv()

DATALAND_URL: Final[str | None] = os.getenv("DATALAND_URL")
DATALAND_API_KEY: Final[str | None] = os.getenv("DATALAND_API_KEY")
REQUEST_TIMEOUT: Final[float] = 30.0


class DatalandConfigError(RuntimeError):
    """Raised when required Dataland configuration is missing."""

    def __init__(self, var_name: str) -> None:
        super().__init__(f"{var_name} is not configured.")


def _build_headers() -> dict[str, str]:
    if not DATALAND_API_KEY:
        raise DatalandConfigError("DATALAND_API_KEY")
    return {"Authorization": f"Bearer {DATALAND_API_KEY}", "accept": "application/json"}


def _get_base_url() -> str:
    if not DATALAND_URL:
        raise DatalandConfigError("DATALAND_URL")
    return DATALAND_URL.rstrip("/")


def download_document(reference_id: str) -> requests.Response:
    """Download document by reference_id."""
    url = f"{_get_base_url()}/documents/{reference_id}"
    response = requests.get(url, headers=_build_headers(), timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response
