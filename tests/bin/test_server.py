from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from dataland_qa_lab.bin.server import dataland_qa_lab

client = TestClient(dataland_qa_lab)


@patch("dataland_qa_lab.bin.server.review_dataset_via_api")
@patch("dataland_qa_lab.bin.server.get_german_time_as_string")
def test_review_dataset_post_endpoint(mock_time: MagicMock, mock_review_api: MagicMock) -> None:
    """Test the /review/{data_id} POST endpoint of the server."""
    mock_time.return_value = "2025-01-01T12:00:00"
    mock_review_api.return_value = {"foo": "bar"}

    data_id = "12345"

    response = client.post(f"/review/{data_id}")

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
