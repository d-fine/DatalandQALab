from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest

from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets


@patch("dataland_qa_lab.dataland.unreviewed_datasets.config.get_config")
class TestUnreviewedDatasets(TestCase):
    @staticmethod
    def set_up_mock_client(dataset_count: int, datasets: list[MagicMock], exception: Exception) -> MagicMock:
        mock_client = MagicMock()

        if exception:
            mock_client.qa_api.get_number_of_pending_datasets.side_effect = exception
        else:
            mock_client.qa_api.get_number_of_pending_datasets.return_value = dataset_count
            mock_client.qa_api.get_info_on_pending_datasets.return_value = datasets or []

        mock_conf = MagicMock()
        mock_conf.dataland_client = mock_client
        return mock_conf

    def test_initialization_with_valid_data(self, mock_get_config: MagicMock) -> None:
        mock_conf = self.set_up_mock_client(
            dataset_count=3,
            datasets=[
                MagicMock(data_id="datasetid1"),
                MagicMock(data_id="datasetid2"),
                MagicMock(data_id="datasetid3"),
            ],
            exception=None,
        )
        mock_get_config.return_value = mock_conf

        unreviewed_datasets = UnreviewedDatasets()
        assert len(unreviewed_datasets.datasets) == 3
        assert unreviewed_datasets.list_of_data_ids == ["datasetid1", "datasetid2", "datasetid3"]

    def test_initialization_with_no_datasets(self, mock_get_config: MagicMock) -> None:
        mock_conf = self.set_up_mock_client(dataset_count=0, datasets=[], exception=None)
        mock_get_config.return_value = mock_conf

        unreviewed_datasets = UnreviewedDatasets()
        assert len(unreviewed_datasets.datasets) == 0
        assert unreviewed_datasets.list_of_data_ids == []

    def test_initialization_with_invalid_number_of_datasets(self, mock_get_config: MagicMock) -> None:
        mock_conf = self.set_up_mock_client(dataset_count=-1, datasets=None, exception=None)
        mock_get_config.return_value = mock_conf

        with pytest.raises(ValueError, match=r"Received an invalid number of pending datasets."):
            UnreviewedDatasets()

    def test_initialization_with_api_error(self, mock_get_config: MagicMock) -> None:
        mock_conf = self.set_up_mock_client(dataset_count=1, datasets=None, exception=Exception())
        mock_get_config.return_value = mock_conf

        with pytest.raises(Exception):  # noqa: B017, PT011
            UnreviewedDatasets()

    def test_initialization_with_timeout_error(self, mock_get_config: MagicMock) -> None:
        mock_conf = self.set_up_mock_client(dataset_count=1, datasets=None, exception=TimeoutError())
        mock_get_config.return_value = mock_conf

        with pytest.raises(TimeoutError):
            UnreviewedDatasets()

    def test_initialization_with_no_client(self, mock_get_config: MagicMock) -> None:  # noqa: PLR6301
        mock_conf = MagicMock()
        mock_conf.dataland_client = None
        mock_get_config.return_value = mock_conf

        with pytest.raises(ValueError, match=r"Client Setup failed in the configuration."):
            UnreviewedDatasets()

    def test_initialization_with_runtime_error(self, mock_get_config: MagicMock) -> None:
        mock_conf = self.set_up_mock_client(dataset_count=1, datasets=None, exception=RuntimeError())
        mock_get_config.return_value = mock_conf

        with pytest.raises(RuntimeError):
            UnreviewedDatasets()
