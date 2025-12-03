from unittest.mock import MagicMock, patch

import pytest
import requests

from monitor.main import run_report_on_qalab


@pytest.fixture
def mock_framework() -> MagicMock:
    return MagicMock()


def test_run_report_on_qalab_success(mock_framework: MagicMock) -> None:
    """Test that the function returns JSON when API call succeeds."""
    mock_json = {"result": "ok"}

    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = mock_json
        mock_post.return_value.raise_for_status = lambda: None

        result = run_report_on_qalab(data_id="123", ai_model="gpt-4", framework=mock_framework)
        assert result == mock_json
        mock_post.assert_called_once()


def test_run_report_on_qalab_failure(mock_framework: MagicMock) -> None:
    """Test that the function raises an error when API call fails."""
    with patch("requests.post", side_effect=requests.HTTPError("Bad Request")), pytest.raises(
        requests.HTTPError
    ):
        run_report_on_qalab(data_id="123", ai_model="gpt-4", framework=mock_framework)
