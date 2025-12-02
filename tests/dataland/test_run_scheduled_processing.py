from unittest.mock import MagicMock, patch

import pytest

from dataland_qa_lab.dataland.scheduled_processor import old_run_scheduled_processing, run_scheduled_processing
from dataland_qa_lab.utils.slack import send_slack_message


@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
@patch("dataland_qa_lab.dataland.scheduled_processor.slack.send_slack_message")
def test_run_scheduled_processing_unreviewed_datasets_error(
    mock_send_slack_message: MagicMock, mock_unreviewed_datasets: MagicMock
) -> None:
    mock_unreviewed_datasets.side_effect = Exception("Error while creating UnreviewedDatasets")
    mock_send_slack_message.return_value = None
    with pytest.raises(Exception) as context:  # noqa: PT011
        old_run_scheduled_processing()
    assert str(context.value) == "Error while creating UnreviewedDatasets"


def test_send_slack_message() -> None:
    with (
        patch("requests.post") as mocked_post,
        patch("dataland_qa_lab.utils.slack.config.get_config") as mocked_get_config,
    ):
        fake_config = type("C", (), {"slack_webhook_url": "https://example.test", "environment": "testenv"})()
        mocked_get_config.return_value = fake_config

        mocked_post.return_value.status_code = 200
        mocked_post.return_value.text = "ok"
        test = send_slack_message(message="test")

    assert test is not None
    assert test.status_code == 200
    assert test.text == "ok"


# test case for new scheduler
@patch("dataland_qa_lab.dataland.scheduled_processor.slack.send_slack_message")
@patch("dataland_qa_lab.dataland.scheduled_processor.config")
def test_run_scheduled_processing_get_info_error(
    mock_config: MagicMock,
    mock_send_slack_message: MagicMock,
) -> None:
    """Test error propagation when get_info_on_datasets() fails."""
    mock_config.dataland_client.qa_api.get_info_on_datasets.side_effect = Exception("Error retrieving datasets")

    mock_send_slack_message.return_value = None
    with pytest.raises(Exception) as exc:
        run_scheduled_processing()

    assert str(exc.value) == "Error retrieving datasets"

    mock_send_slack_message.assert_not_called()
