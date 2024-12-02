import unittest
from unittest.mock import MagicMock, patch
import pytest
from dataland_qa_lab.dataland.scheduled_processor import run_scheduled_processing


class TestRunScheduledProcessing(unittest.TestCase):
    @patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
    def test_run_scheduled_processing(self, mock_unreviewed_datasets: MagicMock) -> None:
        mock_unreviewed_datasets.side_effect = Exception("Error while creating UnreviewedDatasets")

        with pytest.raises(Exception) as context:  # noqa: PT011
            run_scheduled_processing(iterations=1)

        assert str(context.value) == "Error while creating UnreviewedDatasets"

    @patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")  # Mock the UnreviewedDatasets class
    def test_processing_loops(self, mock_unreviewed_datasets: MagicMock) -> None:
        # Set up the mock for UnreviewedDatasets
        mock_instance = MagicMock()
        mock_instance.list_of_data_ids = []  # Simulate empty dataset list
        mock_unreviewed_datasets.return_value = mock_instance

        # Define the number of iterations
        iterations = 5

        # Run the function
        run_scheduled_processing(iterations=iterations)

        # Verify the number of iterations
        assert mock_unreviewed_datasets.call_count == iterations

    @patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")  # Mock the UnreviewedDatasets class
    def test_processing_max_loops(self, mock_unreviewed_datasets: MagicMock) -> None:
        # Set up the mock for UnreviewedDatasets
        mock_instance = MagicMock()
        mock_instance.list_of_data_ids = []  # Simulate empty dataset list
        mock_unreviewed_datasets.return_value = mock_instance

        iterations = 100

        run_scheduled_processing(iterations=iterations)
        assert mock_unreviewed_datasets.call_count == 10
