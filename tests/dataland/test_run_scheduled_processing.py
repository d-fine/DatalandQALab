from unittest.mock import MagicMock, patch

import pytest

from dataland_qa_lab.dataland.alerting import send_alert_message
from dataland_qa_lab.dataland.scheduled_processor import run_scheduled_processing


@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
@patch("dataland_qa_lab.dataland.scheduled_processor.send_alert_message")
def test_run_scheduled_processing_unreviewed_datasets_error(
    mock_send_alert_message: MagicMock, mock_unreviewed_datasets: MagicMock
) -> None:
    mock_unreviewed_datasets.side_effect = Exception("Error while creating UnreviewedDatasets")
    mock_send_alert_message.return_value = None
    with pytest.raises(Exception) as context:  # noqa: PT011
        run_scheduled_processing()
    assert str(context.value) == "Error while creating UnreviewedDatasets"


def test_send_alert_message() -> None:
    with patch("requests.post") as mocked_post, patch(
        "dataland_qa_lab.dataland.alerting.config.get_config"
    ) as mocked_get_config:
        # Provide a fake config object with slack_webhook_url and environment
        fake_config = type("C", (), {"slack_webhook_url": "https://example.test", "environment": "testenv"})()
        mocked_get_config.return_value = fake_config

        mocked_post.return_value.status_code = 200
        mocked_post.return_value.text = "ok"
        test = send_alert_message(message="test")

    assert test is not None
    assert test.status_code == 200
    assert test.text == "ok"
