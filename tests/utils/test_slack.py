from unittest.mock import MagicMock, patch

from dataland_qa_lab.utils.slack import send_slack_message


@patch("dataland_qa_lab.utils.slack.config")
@patch("dataland_qa_lab.utils.slack.sentry_sdk.capture_message")
def test_send_slack_message_success(mock_capture: MagicMock, mock_config: MagicMock) -> None:
    mock_config.get_config.return_value.environment = "dev"

    send_slack_message("Test message")

    mock_capture.assert_called_once_with(
        "Notification: [dev] Test message",
        level="warning",
    )


@patch("dataland_qa_lab.utils.slack.logger")
@patch("dataland_qa_lab.utils.slack.config")
@patch("dataland_qa_lab.utils.slack.sentry_sdk.capture_message")
def test_send_slack_message_failure(
    mock_capture: MagicMock,
    mock_config: MagicMock,
    mock_logger: MagicMock,
) -> None:
    mock_config.get_config.return_value.environment = "dev"
    exc = Exception("Network error")
    mock_capture.side_effect = exc

    send_slack_message("Test message")

    mock_capture.assert_called_once()
    mock_logger.warning.assert_any_call("Failed to send notification to Sentry: %s", exc)
