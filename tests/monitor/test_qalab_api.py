import pytest
from unittest.mock import MagicMock, patch
import requests

from monitor.main import run_report_on_qalab


@pytest.fixture
def mock_framework():
    return MagicMock()


def test_run_report_on_qalab_success(mock_framework) -> None:
    """Test that the function returns JSON when API call succeeds."""
    mock_json = {"result": "ok"}

    # Mock response object
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = mock_json

    with patch("requests.post", return_value=mock_response) as mock_post:
        result = run_report_on_qalab("123", "gpt-4", use_ocr=True, framework=mock_framework)

    assert result == mock_json
    mock_post.assert_called_once()


def test_run_report_on_qalab_failure(mock_framework) -> None:
    """Test that the function raises an error when API call fails."""
    with patch("requests.post", side_effect=requests.HTTPError("Bad Request")), pytest.raises(requests.HTTPError):
        run_report_on_qalab("123", "gpt-4", use_ocr=False, framework=mock_framework)
