from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import RequestException

from qa_lab_monitor import qalab_api


@patch("qa_lab_monitor.qalab_api.requests.get")
def test_check_qalab_api_health_success(mock_get: MagicMock) -> None:
    """Test health check succeeds when requests.get returns 200."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    qalab_api.check_qalab_api_health()
    mock_get.assert_called_once_with(f"{qalab_api.config.qa_lab_url}/health", timeout=10)
    mock_response.raise_for_status.assert_called_once()


@patch("qa_lab_monitor.qalab_api.requests.get")
def test_check_qalab_api_health_failure(mock_get: MagicMock) -> None:
    """Test health check exits when requests.get fails."""

    mock_get.side_effect = RequestException("API down")

    with pytest.raises(SystemExit) as e:
        qalab_api.check_qalab_api_health()
    assert e.type is SystemExit
    assert e.value.code == 1


@patch("qa_lab_monitor.qalab_api.requests.post")
def test_review_data_point_on_qalab_success(mock_post: MagicMock) -> None:
    """Test that review_data_point_on_qalab returns JSON data correctly."""
    sample_data_point_id = "dp123"
    sample_ai_model = "test-model"
    sample_use_ocr = False

    mock_response = MagicMock()
    mock_response.json.return_value = {"qa_status": "Accepted", "confidence": 0.95}
    mock_response.text = '{"qa_status": "Accepted", "confidence": 0.95}'
    mock_response.url = "http://fake.url"
    mock_post.return_value = mock_response

    result = qalab_api.review_data_point_on_qalab(sample_data_point_id, sample_ai_model, sample_use_ocr)

    expected_url = f"{qalab_api.config.qa_lab_url}/review-data-point/{sample_data_point_id}"
    mock_post.assert_called_once_with(
        expected_url, params={"ai_model": sample_ai_model, "use_ocr": sample_use_ocr, "override": False}, timeout=120
    )

    assert result == {"qa_status": "Accepted", "confidence": 0.95}
