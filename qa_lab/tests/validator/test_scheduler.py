from unittest.mock import MagicMock, patch

from qa_lab.dataland.api import QaStatus
from qa_lab.validator.scheduler import run_scheduled_processing

mock_conf = MagicMock()
mock_conf.ai_model = "test-model"
mock_conf.use_ocr = True


@patch("qa_lab.validator.scheduler.get_pending_datasets", return_value=[])
@patch("qa_lab.validator.scheduler.get_config", return_value=mock_conf)
def test_no_pending_datasets(mock_get_config: MagicMock, mock_get_pending: MagicMock) -> None:  # noqa: ARG001
    """Test that no processing occurs when there are no pending datasets."""
    run_scheduled_processing()
    mock_get_pending.assert_called_once()


@patch("qa_lab.validator.scheduler.set_dataset_status")
@patch("qa_lab.validator.scheduler.validate_datapoint")
@patch("qa_lab.validator.scheduler.get_dataset_data_points")
@patch("qa_lab.validator.scheduler.get_pending_datasets")
@patch("qa_lab.validator.scheduler.get_config", return_value=mock_conf)
def test_some_data_points_rejected(
    mock_get_config: MagicMock,  # noqa: ARG001
    mock_get_pending: MagicMock,
    mock_get_data_points: MagicMock,
    mock_validate: MagicMock,
    mock_set_status: MagicMock,
) -> None:
    """Test that datasets with some rejected data points are marked as Rejected."""
    dataset = {"dataId": "ds2"}
    mock_get_pending.return_value = [dataset]
    mock_get_data_points.return_value = {"type1": "dp1", "type2": "dp2"}

    mock_validate.side_effect = [{"qa_status": "Accepted"}, {"qa_status": "Rejected"}]

    run_scheduled_processing()

    mock_set_status.assert_called_once_with("ds2", QaStatus.Rejected)


@patch("qa_lab.validator.scheduler.set_dataset_status")
@patch("qa_lab.validator.scheduler.validate_datapoint")
@patch("qa_lab.validator.scheduler.get_dataset_data_points")
@patch("qa_lab.validator.scheduler.get_pending_datasets")
@patch("qa_lab.validator.scheduler.get_config", return_value=mock_conf)
def test_validate_datapoint_exception(
    mock_get_config: MagicMock,  # noqa: ARG001
    mock_get_pending: MagicMock,
    mock_get_data_points: MagicMock,
    mock_validate: MagicMock,
    mock_set_status: MagicMock,  # noqa: ARG001
) -> None:
    """Test that exceptions in validate_datapoint are handled gracefully."""
    dataset = {"dataId": "ds3"}
    mock_get_pending.return_value = [dataset]
    mock_get_data_points.return_value = {"type1": "dp1"}

    mock_validate.side_effect = Exception("Test error")

    run_scheduled_processing()
