from unittest.mock import MagicMock, patch

import pytest
import requests

from monitor.qalab_api import check_qalab_api_health, run_report_on_qalab


def test_check_qalab_api_health_success() -> None:
    """Test that the function completes without exiting when API is healthy."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        check_qalab_api_health()


def test_check_qalab_api_health_failure() -> None:
    """Test that the function exits when API call fails."""
    with patch("requests.get", side_effect=requests.ConnectionError("API failure")):
        with pytest.raises(SystemExit) as exit_info:
            check_qalab_api_health()

        # Ensure sys.exit(1) was called
        assert exit_info.value.code == 1


def test_run_report_on_qalab_success() -> None:
    """Test that the function returns JSON when API call succeeds."""
    mock_json = {"result": "ok"}

    # Mock response object
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = mock_json

    with patch("requests.post", return_value=mock_response) as mock_get:
        result = run_report_on_qalab("123", "gpt-4", True)

    # Assertions
    mock_get.assert_called_once()
    assert result == mock_json


def test_run_report_on_qalab_failure() -> None:
    """Test that the function raises an error when API call fails."""
    with patch("requests.post", side_effect=requests.HTTPError("Bad Request")), pytest.raises(requests.HTTPError):
        run_report_on_qalab("123", "gpt-4", False)
