from unittest.mock import MagicMock, patch

from dataland_qa_lab.utils.slack import send_slack_message


@patch("dataland_qa_lab.utils.slack.requests.post")
def test_send_slack_message_success(mock_request: MagicMock) -> None:
    """Test sending a Slack message successfully."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_request.return_value = mock_response

    send_slack_message("Test message")

    mock_request.assert_called_once()
    _args, kwargs = mock_request.call_args

    assert kwargs["url"]
    assert kwargs["json"] == {"text": "Test message"}


@patch("dataland_qa_lab.utils.slack.requests.request")
def test_send_slack_message_failure(mock_request: MagicMock) -> None:
    """Test handling of a failed Slack message send."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Error"
    mock_request.return_value = mock_response

    send_slack_message("Failing message")
