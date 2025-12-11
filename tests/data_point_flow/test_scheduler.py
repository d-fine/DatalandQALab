from unittest.mock import MagicMock, patch

import pytest
from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import review, scheduler


@pytest.mark.parametrize(
    ("validator_result", "expected_accepted", "expected_rejected", "expected_not_validated"),
    [
        (
            review.models.ValidatedDatapoint(
                data_point_id="dp1",
                data_point_type="number",
                previous_answer=None,
                predicted_answer="42",
                confidence=0.9,
                reasoning="ok",
                qa_status=QaStatus.ACCEPTED,
                timestamp=1,
                ai_model="gpt-4",
                use_ocr=True,
                file_name="file.pdf",
                file_reference="ref1",
                page=1,
                override=False,
            ),
            1,
            0,
            0,
        ),
        (
            review.models.ValidatedDatapoint(
                data_point_id="dp2",
                data_point_type="number",
                previous_answer=None,
                predicted_answer="wrong",
                confidence=0.5,
                reasoning="mismatch",
                qa_status=QaStatus.REJECTED,
                timestamp=1,
                ai_model="gpt-4",
                use_ocr=True,
                file_name="file.pdf",
                file_reference="ref2",
                page=1,
                override=False,
            ),
            0,
            1,
            0,
        ),
        (
            review.models.CannotValidateDatapoint(
                data_point_id="dp3",
                data_point_type=None,
                reasoning="error",
                ai_model="gpt-4",
                use_ocr=True,
                override=False,
                timestamp=1,
            ),
            0,
            0,
            1,
        ),
    ],
)
@patch("dataland_qa_lab.data_point_flow.scheduler.slack.send_slack_message")
@patch("dataland_qa_lab.data_point_flow.scheduler.config")
@patch("dataland_qa_lab.data_point_flow.scheduler.review.validate_datapoint")
def test_run_scheduled_processing(  # noqa: PLR0913, PLR0917
    mock_validate: MagicMock,
    mock_config: MagicMock,
    mock_slack: MagicMock,
    validator_result: MagicMock,
    expected_accepted: int,
    expected_rejected: int,
    expected_not_validated: int,
) -> None:
    """Test run_scheduled_processing with different validator responses."""

    mock_config.dataland_client.qa_api.get_info_on_datasets.return_value = [MagicMock(data_id="dataset1")]
    mock_config.dataland_client.meta_api.get_contained_data_points.return_value = {"number": "dp1"}
    mock_config.ai_model = "gpt-4"
    mock_config.use_ocr = True
    mock_config.frameworks_list = ["number"]

    mock_validate.return_value = validator_result

    scheduler.run_scheduled_processing()

    assert mock_slack.called
    sent_message = mock_slack.call_args[0][0]
    assert f"Accepted {expected_accepted}" in sent_message
    assert f"Rejected {expected_rejected}" in sent_message
    assert f"Not validated {expected_not_validated}" in sent_message

    mock_config.dataland_client.qa_api.change_qa_status.assert_called_once_with(
        data_id="dataset1", qa_status=QaStatus.PENDING, overwrite_data_point_qa_status=False
    )
