from unittest.mock import MagicMock, patch

import pytest

from dataland_qa_lab.utils.slack import send_slack_message


@patch("dataland_qa_lab.utils.slack.config")
@patch("dataland_qa_lab.utils.slack.requests.post")
def test_send_slack_message_success(mock_post: MagicMock, mock_config: MagicMock) -> None:
    """Test sending a Slack message successfully."""
    mock_config.get_config.return_value.slack_webhook_url = "https://hooks.slack.com/services/"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    send_slack_message("Test message")
    mock_post.assert_called_once()


@patch("dataland_qa_lab.utils.slack.config")
@patch("dataland_qa_lab.utils.slack.requests.post")
def test_send_slack_message_failure(mock_post: MagicMock, mock_config: MagicMock) -> None:
    """Test handling of a failed Slack message send."""
    mock_config.get_config.return_value.slack_webhook_url = "https://hooks.slack.com/services/"
    mock_post.side_effect = Exception("Network error")
    with pytest.raises(Exception, match="Network error"):
        send_slack_message("Test message")

    mock_post.assert_called_once()
