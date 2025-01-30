from unittest.mock import MagicMock, patch

from dataland_qa_lab.dataland.scheduled_processor import run_scheduled_processing


@patch("dataland_qa_lab.dataland.scheduled_processor.time.sleep")  # Mock time.sleep to avoid delays
@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
def test_run_scheduled_processing_loops(mock_unreviewed_datasets: MagicMock, mock_sleep) -> None:  # noqa: ANN001
    mock_instance = MagicMock()
    mock_instance.list_of_data_ids = []
    mock_unreviewed_datasets.return_value = mock_instance

    iterations = 5
    run_scheduled_processing(iterations=iterations)

    # Assert that UnreviewedDatasets was called the expected number of times
    assert mock_unreviewed_datasets.call_count == iterations
    # Assert that time.sleep was called the expected number of times
    assert mock_sleep.call_count == iterations


@patch("dataland_qa_lab.dataland.scheduled_processor.time.sleep")
@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
def test_run_scheduled_processing_max_loops(mock_unreviewed_datasets: MagicMock, mock_sleep: MagicMock) -> None:
    mock_instance = MagicMock()
    mock_instance.list_of_data_ids = []
    mock_unreviewed_datasets.return_value = mock_instance

    mock_sleep.side_effect = lambda x: x if x <= 5 else None

    iterations = 10
    run_scheduled_processing(iterations=iterations)

    # Assert that UnreviewedDatasets was called 10 times (maximum iterations)
    assert mock_unreviewed_datasets.call_count == 10
    # Assert that time.sleep was called 10 times (once per iteration)
    assert mock_sleep.call_count == 10


@patch("dataland_qa_lab.dataland.scheduled_processor.time.sleep")
@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
@patch("dataland_qa_lab.dataland.scheduled_processor.review_dataset")
def test_run_scheduled_processing_with_datasets(
    mock_review_dataset: MagicMock, mock_unreviewed_datasets: MagicMock, mock_sleep: MagicMock
) -> None:
    mock_instance = MagicMock()
    mock_instance.list_of_data_ids = ["dataset1", "dataset2"]
    mock_unreviewed_datasets.return_value = mock_instance

    run_scheduled_processing(iterations=1)

    # Assert that review_dataset was called for each dataset ID
    assert mock_review_dataset.call_count == 2
    mock_review_dataset.assert_any_call("dataset1")
    mock_review_dataset.assert_any_call("dataset2")

    # Assert that the dataset IDs were removed after processing
    assert len(mock_instance.list_of_data_ids) == 0

    # Assert that UnreviewedDatasets was called once
    assert mock_unreviewed_datasets.call_count == 1

    # Assert that time.sleep was called once
    assert mock_sleep.call_count == 0
