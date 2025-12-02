from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.dataland import scheduled_processor


def create_mock_dataset(data_id: str, data_points: dict) -> tuple[SimpleNamespace, dict]:
    """Mock dataset and its data points."""
    dataset = SimpleNamespace(data_id=data_id)
    return dataset, data_points


@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
@patch("dataland_qa_lab.dataland.scheduled_processor.dataset_reviewer.old_review_dataset")
@patch("dataland_qa_lab.dataland.scheduled_processor.slack.send_slack_message")
def test_old_run_scheduled_processing_success(
    mock_slack: MagicMock, mock_review: MagicMock, mock_unreviewed: MagicMock
) -> None:
    """Test old_run_scheduled_processing with successful reviews."""
    mock_dataset = MagicMock()
    mock_dataset.list_of_data_ids = ["id1", "id2"]
    mock_unreviewed.return_value = mock_dataset

    scheduled_processor.old_run_scheduled_processing()

    assert mock_review.call_count == 2
    mock_slack.assert_not_called()


@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
@patch("dataland_qa_lab.dataland.scheduled_processor.dataset_reviewer.old_review_dataset")
@patch("dataland_qa_lab.dataland.scheduled_processor.slack.send_slack_message")
def test_old_run_scheduled_processing_review_error(
    mock_slack: MagicMock, mock_review: MagicMock, mock_unreviewed: MagicMock
) -> None:
    """Test old_run_scheduled_processing when a review raises an exception."""
    mock_dataset = MagicMock()
    mock_dataset.list_of_data_ids = ["id1"]
    mock_unreviewed.return_value = mock_dataset
    mock_review.side_effect = Exception("review failed")

    scheduled_processor.old_run_scheduled_processing()

    mock_review.assert_called_once_with("id1")
    mock_slack.assert_called_once()


@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
def test_old_run_scheduled_processing_no_datasets(mock_unreviewed: MagicMock) -> None:
    """Test old_run_scheduled_processing when there are no unreviewed datasets."""
    mock_dataset = MagicMock()
    mock_dataset.list_of_data_ids = []
    mock_unreviewed.return_value = mock_dataset

    scheduled_processor.old_run_scheduled_processing()


@patch("dataland_qa_lab.dataland.scheduled_processor.config")
def test_run_scheduled_processing_no_datasets(mock_config: MagicMock) -> None:
    """Test run_scheduled_processing when there are no unreviewed datasets."""
    mock_client = MagicMock()
    mock_client.qa_api.get_info_on_datasets.return_value = []
    mock_client.meta_api.get_contained_data_points.return_value = {}

    mock_config.dataland_client = mock_client
    mock_config.ai_model = "gpt"
    mock_config.use_ocr = True
    mock_config.frameworks_list = []

    with patch("dataland_qa_lab.dataland.scheduled_processor.slack.send_slack_message") as slack_mock:
        scheduled_processor.run_scheduled_processing()

        slack_mock.assert_not_called()
        mock_client.qa_api.change_qa_status.assert_not_called()


@patch("dataland_qa_lab.dataland.scheduled_processor.config")
@patch("dataland_qa_lab.dataland.scheduled_processor.dataset_reviewer.validate_datapoint")
@patch("dataland_qa_lab.dataland.scheduled_processor.database_engine.get_entity", return_value=None)
@patch("dataland_qa_lab.dataland.scheduled_processor.database_engine.add_entity")
@patch("dataland_qa_lab.dataland.scheduled_processor.slack.send_slack_message")
def test_run_scheduled_processing_all_accepted(
    mock_slack: MagicMock, mock_add: MagicMock, mock_get: MagicMock, mock_validate: MagicMock, mock_config: MagicMock
) -> None:
    """Test run_scheduled_processing where all datapoints are accepted."""
    dataset, datapoints = create_mock_dataset("ds1", {"A": "dp1", "B": "dp2"})
    mock_validate.return_value = SimpleNamespace(qa_status=QaStatus.ACCEPTED)

    mock_client = MagicMock()
    mock_client.qa_api.get_info_on_datasets.return_value = [dataset]
    mock_client.meta_api.get_contained_data_points.return_value = datapoints

    mock_config.dataland_client = mock_client
    mock_config.ai_model = "gpt"
    mock_config.use_ocr = True
    mock_config.frameworks_list = []

    scheduled_processor.run_scheduled_processing()

    mock_client.qa_api.change_qa_status.assert_called_once_with(
        data_id="ds1",
        qa_status=QaStatus.ACCEPTED,
        overwrite_data_point_qa_status=False,
    )

    slack_text = mock_slack.call_args[0][0]
    assert "🎉 Dataset ID: ds1 accepted" in slack_text
    assert "dp1" in slack_text
    assert "dp2" in slack_text


@patch("dataland_qa_lab.dataland.scheduled_processor.config")
@patch("dataland_qa_lab.dataland.scheduled_processor.dataset_reviewer.validate_datapoint")
@patch("dataland_qa_lab.dataland.scheduled_processor.database_engine.get_entity", return_value=None)
@patch("dataland_qa_lab.dataland.scheduled_processor.database_engine.add_entity")
@patch("dataland_qa_lab.dataland.scheduled_processor.slack.send_slack_message")
def test_run_scheduled_processing_mixed(
    mock_slack: MagicMock, mock_add: MagicMock, mock_get: MagicMock, mock_validate: MagicMock, mock_config: MagicMock
) -> None:
    """Test run_scheduled_processing where some datapoints are rejected."""
    dataset, datapoints = create_mock_dataset("ds2", {"type1": "dp1", "type2": "dp2"})

    def validate_side_effect(dp, **_):
        if dp == "dp1":
            return SimpleNamespace(qa_status=QaStatus.ACCEPTED)
        return SimpleNamespace(qa_status=QaStatus.REJECTED)

    mock_validate.side_effect = validate_side_effect

    mock_client = MagicMock()
    mock_client.qa_api.get_info_on_datasets.return_value = [dataset]
    mock_client.meta_api.get_contained_data_points.return_value = datapoints

    mock_config.dataland_client = mock_client
    mock_config.ai_model = "gpt"
    mock_config.use_ocr = True
    mock_config.frameworks_list = []

    scheduled_processor.run_scheduled_processing()

    mock_client.qa_api.change_qa_status.assert_called_once_with(
        data_id="ds2",
        qa_status=QaStatus.REJECTED,
        overwrite_data_point_qa_status=False,
    )

    slack_text = mock_slack.call_args[0][0]
    assert "❌ Data point ID: dp2" in slack_text
    assert "⚠️ Dataset ID: ds2 rejected" in slack_text or "rejected with" in slack_text


@patch("dataland_qa_lab.dataland.scheduled_processor.config")
@patch("dataland_qa_lab.dataland.scheduled_processor.dataset_reviewer.validate_datapoint")
@patch("dataland_qa_lab.dataland.scheduled_processor.database_engine.get_entity", return_value=None)
@patch("dataland_qa_lab.dataland.scheduled_processor.database_engine.add_entity")
@patch("dataland_qa_lab.dataland.scheduled_processor.slack.send_slack_message")
def test_run_scheduled_processing_exception(
    mock_slack: MagicMock, mock_add: MagicMock, mock_get: MagicMock, mock_validate: MagicMock, mock_config: MagicMock
) -> None:
    """Test run_scheduled_processing where validation raises an exception."""
    dataset, datapoints = create_mock_dataset("ds3", {"only": "dp1"})
    mock_validate.side_effect = Exception("validation error")

    mock_client = MagicMock()
    mock_client.qa_api.get_info_on_datasets.return_value = [dataset]
    mock_client.meta_api.get_contained_data_points.return_value = datapoints

    mock_config.dataland_client = mock_client
    mock_config.ai_model = "gpt"
    mock_config.use_ocr = True
    mock_config.frameworks_list = []

    scheduled_processor.run_scheduled_processing()

    mock_client.qa_api.change_qa_status.assert_called_once_with(
        data_id="ds3",
        qa_status=QaStatus.REJECTED,
        overwrite_data_point_qa_status=False,
    )

    slack_text = mock_slack.call_args[0][0]
    assert "🟡 Couldn't find a verdict" in slack_text
