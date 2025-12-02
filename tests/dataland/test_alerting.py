from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import ConnectionError as RequestsConnectionError

from dataland_qa_lab.dataland.alerting import send_alert_message


@pytest.fixture
def mock_deps() -> Generator[tuple[MagicMock, MagicMock], None, None]:
    """Mock dependencies for alerting tests."""
    with (
        patch("dataland_qa_lab.dataland.alerting.config.get_config") as mock_config,
        patch("dataland_qa_lab.dataland.alerting.requests.post") as mock_post,
    ):
        mock_config.return_value.slack_webhook_url = "http://fake-webhook-url"
        mock_config.return_value.environment = "test-environment"
        yield mock_config, mock_post


def test_send_alert_message_success(mock_deps: tuple[MagicMock, MagicMock]) -> None:
    """Test successful sending of alert message."""
    _mock_config, mock_post = mock_deps

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    response = send_alert_message("Test alert message")

    assert response is not None
    assert response.status_code == 200

    mock_response.raise_for_status.assert_called_once()

    mock_post.assert_called_once()
    _args, kwargs = mock_post.call_args
    assert kwargs["json"] == {"text": "[test-environment] Test alert message"}


def test_send_alert_message_no_url(mock_deps: tuple[MagicMock, MagicMock], caplog: pytest.LogCaptureFixture) -> None:
    """Test sending alert message when webhook URL is missing."""
    mock_config, _mock_post = mock_deps
    mock_config.return_value.slack_webhook_url = None

    response = send_alert_message("Message without URL")

    assert response is None
    assert "Slack webhook URL is missing in the configuration" in caplog.text


def test_send_alert_message_network_error(
    mock_deps: tuple[MagicMock, MagicMock], caplog: pytest.LogCaptureFixture
) -> None:
    """Test sending alert message when a network error occurs."""
    _mock_config, mock_post = mock_deps

    mock_post.side_effect = RequestsConnectionError("Network error")
    response = send_alert_message("Message with network error")

    assert response is None
    assert "Failed to send alert message to Slack" in caplog.text
