from unittest.mock import MagicMock, patch

import pytest

from dataland_qa_lab.dataland.scheduled_processor import run_scheduled_processing


@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
def test_run_scheduled_processing_unreviewed_datasets_error(mock_unreviewed_datasets: MagicMock) -> None:
    mock_unreviewed_datasets.side_effect = Exception("Error while creating UnreviewedDatasets")
    with pytest.raises(Exception) as context:  # noqa: PT011
        run_scheduled_processing(iterations=1)
    assert str(context.value) == "Error while creating UnreviewedDatasets"


@patch("dataland_qa_lab.dataland.scheduled_processor.time.sleep")  # Mock time.sleep to avoid delays
@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
def test_run_scheduled_processing_loops(mock_unreviewed_datasets: MagicMock, mock_sleep) -> None:  # noqa: ANN001
    mock_instance = MagicMock()
    mock_instance.list_of_data_ids = []
    mock_unreviewed_datasets.return_value = mock_instance

    iterations = 5
    run_scheduled_processing(iterations=iterations)
    assert mock_unreviewed_datasets.call_count == iterations
    assert mock_sleep.call_count == iterations - 1


@patch("dataland_qa_lab.dataland.scheduled_processor.time.sleep")
@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
def test_run_scheduled_processing_max_loops(mock_unreviewed_datasets: MagicMock, mock_sleep: MagicMock) -> None:
    mock_instance = MagicMock()
    mock_instance.list_of_data_ids = []
    mock_unreviewed_datasets.return_value = mock_instance

    mock_sleep.side_effect = lambda x: x if x <= 5 else None

    iterations = 100
    run_scheduled_processing(iterations=iterations)
    assert mock_unreviewed_datasets.call_count == 10
