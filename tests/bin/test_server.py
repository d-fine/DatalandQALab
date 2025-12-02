from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


<<<<<<< HEAD
=======
def client() -> TestClient:
    """Generate a test client, without building a real database connection"""
    with (
        patch("dataland_qa_lab.database.database_engine.verify_database_connection"),
        patch("dataland_qa_lab.database.database_engine.create_tables"),
    ):
        from dataland_qa_lab.bin.server import dataland_qa_lab  # noqa: PLC0415

        return TestClient(dataland_qa_lab)

>>>>>>> origin/main

@pytest.fixture
def client():  # noqa: ANN201
    return TestClient(dataland_qa_lab)


def test_health_check(client: MagicMock) -> None:
    """Test the /health endpoint of the server."""
    test_client = client()
    response = test_client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"

    assert "timestamp" in data
    assert isinstance(data["timestamp"], str)


@patch("dataland_qa_lab.bin.server.dataset_reviewer.old_review_dataset_via_api")
@patch("dataland_qa_lab.bin.server.get_german_time_as_string")
def test_review_dataset_post_endpoint(mock_time: MagicMock, mock_review_api: MagicMock, client: MagicMock) -> None:
    """Test the /review/{data_id} POST endpoint of the server."""
    mock_time.return_value = "2025-01-01T12:00:00"
    mock_review_api.return_value = {"foo": "bar"}

    data_id = "12345"

    body = {"force_review": False, "ai_model": "gpt-4o", "use_ocr": True}

    test_client = client()
    response = test_client.post(f"/review/{data_id}", json=body)

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


def test_review_data_point_post_endpoint(client: MagicMock) -> None:
    """Test the /review-data-point/{data_point_id} POST endpoint."""
    with patch("dataland_qa_lab.bin.server.dataset_reviewer.validate_datapoint") as mock_validate:
        mock_validate.return_value = SimpleNamespace(
            data_point_id="dp-1",
            data_point_type="text",
            previous_answer="old",
            predicted_answer="new",
            confidence=0.95,
            reasoning="model reasoning",
            qa_status="REVIEWED",
            timestamp="2025-01-01T12:00:00",
            ai_model="gpt-4o",
            use_ocr=True,
            file_reference="abcde",
            file_name="File.pdf",
            page=2,
        )

        data_point_id = "dp-1"

        body = {"ai_model": "gpt-4o", "use_ocr": True, "override": False}

        response = client.post(f"/review-data-point/{data_point_id}", json=body)

        assert response.status_code == 200
        json_resp = response.json()

        assert json_resp["data_point_id"] == "dp-1"
        assert json_resp["data_point_type"] == "text"
        assert json_resp["previous_answer"] == "old"
        assert json_resp["predicted_answer"] == "new"
        assert json_resp["confidence"] == 0.95
        assert json_resp["reasoning"] == "model reasoning"
        assert json_resp["qa_status"] == "REVIEWED"
        assert json_resp["timestamp"] == "2025-01-01T12:00:00"
        assert json_resp["ai_model"] == "gpt-4o"
        assert json_resp["use_ocr"] is True
        assert json_resp["file_reference"] == "abcde"
        assert json_resp["file_name"] == "File.pdf"
        assert json_resp["page"] == 2

        mock_validate.assert_called_once_with(
            data_point_id="dp-1",
            ai_model="gpt-4o",
            use_ocr=True,
            override=False,
        )
