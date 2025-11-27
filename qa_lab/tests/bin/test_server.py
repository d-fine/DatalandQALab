from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from qa_lab.bin.server import qa_lab

client = TestClient(qa_lab)
# test_health.py


def test_health_check() -> None:
    """Test the /health endpoint of the server."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"

    assert "timestamp" in data
    assert isinstance(data["timestamp"], int)


@pytest.fixture
def mock_validate() -> Generator[None, Any, Any]:
    """Mock the validate_datapoint function."""
    with patch("qa_lab.bin.server.validate_datapoint") as mock_fn:
        mock_fn.return_value = {"status": "ok", "id": "123"}
        yield mock_fn


def test_review_datapoint_success(mock_validate: MagicMock) -> None:
    """Test the /review-datapoint/{data_point_id} endpoint of the server."""
    data_point_id = "123"
    ai_model = "gpt-test"

    response = client.post(
        f"/review-datapoint/{data_point_id}",
        params={"ai_model": ai_model, "use_ocr": True, "override": False},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "id": "123"}

    # validate that the function was called correctly
    mock_validate.assert_called_once_with(
        data_point_id=data_point_id,
        ai_model=ai_model,
        use_ocr=True,
        override=False,
    )
