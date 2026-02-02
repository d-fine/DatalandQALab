from unittest.mock import MagicMock, patch

from dataland_qa_lab.utils.slack import send_slack_message


@patch("dataland_qa_lab.utils.slack.sentry_sdk.push_scope")
@patch("dataland_qa_lab.utils.slack.sentry_sdk.capture_message")
@patch("dataland_qa_lab.utils.slack.config")
def test_send_slack_message_success(
    mock_config: MagicMock, mock_capture: MagicMock, mock_push_scope: MagicMock
) -> None:
    mock_config.get_config.return_value.environment = "dev"

    scope = MagicMock()
    cm = MagicMock()
    cm.__enter__.return_value = scope
    cm.__exit__.return_value = None
    mock_push_scope.return_value = cm

    send_slack_message("Test message")

    mock_capture.assert_called_once_with("[DEV] Test message", level="info")
    scope.set_tag.assert_called_once_with("notify", "slack")
    assert scope.fingerprint[0] == "slack-notify"


@patch("dataland_qa_lab.utils.slack.sentry_sdk.push_scope")
@patch("dataland_qa_lab.utils.slack.logger")
@patch("dataland_qa_lab.utils.slack.config")
@patch("dataland_qa_lab.utils.slack.sentry_sdk.capture_message")
def test_send_slack_message_failure(
    mock_capture: MagicMock,
    mock_config: MagicMock,
    mock_logger: MagicMock,
    mock_push_scope: MagicMock,
) -> None:
    mock_config.get_config.return_value.environment = "dev"

    scope = MagicMock()
    cm = MagicMock()
    cm.__enter__.return_value = scope
    cm.__exit__.return_value = None
    mock_push_scope.return_value = cm

    exc = Exception("Network error")
    mock_capture.side_effect = exc

    send_slack_message("Test message")

    mock_capture.assert_called_once()
    mock_logger.warning.assert_any_call("Failed to send notification to Sentry: %s", exc)
