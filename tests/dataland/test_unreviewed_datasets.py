from unittest import TestCase
from unittest.mock import patch, MagicMock
from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets


@patch('dataland_qa_lab.dataland.unreviewed_datasets.config.get_config')
class TestUnreviewedDatasets(TestCase):
    def setUpMockClient(self, dataset_count=None, datasets=None, exception=None):
        mock_client = MagicMock()

        if exception:
            mock_client.qa_api.get_number_of_pending_datasets.side_effect = exception
        else:
            mock_client.qa_api.get_number_of_pending_datasets.return_value = dataset_count
            mock_client.qa_api.get_info_on_pending_datasets.return_value = datasets or []

        mock_conf = MagicMock()
        mock_conf.dataland_client = mock_client
        return mock_conf

    def test_initialization_with_valid_data(self, mock_get_config):
        mock_conf = self.setUpMockClient(
            dataset_count=3,
            datasets=[
                MagicMock(data_id="datasetid1"),
                MagicMock(data_id="datasetid2"),
                MagicMock(data_id="datasetid3"),
            ]
        )
        mock_get_config.return_value = mock_conf

        unreviewed_datasets = UnreviewedDatasets()
        self.assertEqual(len(unreviewed_datasets.datasets), 3)
        self.assertEqual(unreviewed_datasets.list_of_data_ids, ["datasetid1", "datasetid2", "datasetid3"])

    def test_initialization_with_no_datasets(self, mock_get_config):
        mock_conf = self.setUpMockClient(dataset_count=0, datasets=[])
        mock_get_config.return_value = mock_conf

        unreviewed_datasets = UnreviewedDatasets()
        self.assertEqual(len(unreviewed_datasets.datasets), 0)
        self.assertEqual(unreviewed_datasets.list_of_data_ids, [])

    def test_initialization_with_invalid_number_of_datasets(self, mock_get_config):
        mock_conf = self.setUpMockClient(dataset_count=-1)
        mock_get_config.return_value = mock_conf

        with self.assertRaises(ValueError):
            UnreviewedDatasets()

    def test_initialization_with_api_error(self, mock_get_config):
        mock_conf = self.setUpMockClient(exception=Exception("API Error"))
        mock_get_config.return_value = mock_conf

        with self.assertRaises(Exception) as context:
            UnreviewedDatasets()
        self.assertEqual(str(context.exception), "API Error")
