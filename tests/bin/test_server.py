from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from dataland_qa_lab.bin.server import dataland_qa_lab

client = TestClient(dataland_qa_lab)


def test_health_check() -> None:
    """Test the /health endpoint of the server."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"

    assert "timestamp" in data
    assert isinstance(data["timestamp"], str)


@patch("dataland_qa_lab.bin.server.dataset_reviewer.old_review_dataset_via_api")
@patch("dataland_qa_lab.bin.server.get_german_time_as_string")
def test_review_dataset_post_endpoint(mock_time: MagicMock, mock_review_api: MagicMock) -> None:
    """Test the /review/{data_id} POST endpoint of the server."""
    mock_time.return_value = "2025-01-01T12:00:00"
    mock_review_api.return_value = {"foo": "bar"}

    data_id = "12345"

    body = {"force_review": False, "ai_model": "gpt-4o", "use_ocr": True}

    response = client.post(f"/review/{data_id}", json=body)

    assert response.status_code == 200

    json_resp = response.json()

    assert json_resp["data"] == {"foo": "bar"}

    assert json_resp["meta"]["timestamp"] == "2025-01-01T12:00:00"
    assert json_resp["meta"]["ai_model"] == "gpt-4o"
    assert json_resp["meta"]["force_review"] is False
    assert json_resp["meta"]["use_ocr"] is True

    mock_review_api.assert_called_once_with(
        data_id="12345",
        force_review=False,
        ai_model="gpt-4o",
        use_ocr=True,
    )


@pytest.fixture
def mock_validate_datapoint() -> None:
    """Mock dataset_reviewer.validate_datapoint()"""
    with patch("dataland_qa_lab.bin.server.dataset_reviewer.validate_datapoint") as mock:
        mock_res = MagicMock()
        mock_res.data_point_id = "123"
        mock_res.data_point_type = "text"
        mock_res.previous_answer = "old"
        mock_res.predicted_answer = "new"
        mock_res.confidence = 0.95
        mock_res.reasoning = "model reasoning"
        mock_res.qa_status = "reviewed"
        mock_res.timestamp = 12345
        mock_res.ai_model = "gpt-4"
        mock_res.use_ocr = False
        mock_res.file_reference = "file-1"
        mock_res.file_name = "sample.pdf"
        mock_res.page = 2

        mock.return_value = mock_res
        yield mock


def test_review_data_point_success(mock_validate_datapoint: MagicMock) -> None:
    """Test the /review-data-point/{data_point_id} POST endpoint of the server."""
    payload = {"ai_model": "gpt-4", "use_ocr": False, "override": False}

    response = client.post("/review-data-point/123", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["data_point_id"] == "123"
    assert data["predicted_answer"] == "new"
    assert data["confidence"] == 0.95
    assert data["qa_status"] == "reviewed"
    assert data["file_name"] == "sample.pdf"

    # Ensure the mock was called correctly
    mock_validate_datapoint.assert_called_once_with(
        data_point_id="123", ai_model="gpt-4", use_ocr=False, override=False
    )


def test_review_data_point_internal_error() -> None:
    """Test that exceptions inside the handler produce a 500 response."""
    with patch("dataland_qa_lab.bin.server.dataset_reviewer.validate_datapoint") as mock:
        mock.side_effect = Exception("Something went wrong")

        payload = {"ai_model": "gpt-4", "use_ocr": False, "override": False}

        response = client.post("/review-data-point/123", json=payload)

        assert response.status_code == 500
        assert "Something went wrong" in response.json()["detail"]
