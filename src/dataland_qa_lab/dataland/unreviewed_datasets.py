from dataland_qa_lab.utils import config

class UnreviewedDatasets:
    """Class representing the unreviewed datasets from the API."""

    def __init__(self):

        self.conf = config.get_config()
        self.dataland_client = self.conf.dataland_client

        try:
            number_of_datasets = self.dataland_client.qa_api.get_number_of_pending_datasets()
            if number_of_datasets is None or number_of_datasets < 0:
                raise ValueError("Received an invalid number of pending datasets.")

            self.datasets = self.dataland_client.qa_api.get_info_on_pending_datasets(
                data_types=["nuclear-and-gas"], chunk_size=number_of_datasets
            )

            self.list_of_data_ids = [dataset.data_id for dataset in self.datasets]

        except Exception as e:
            print(f"Error fetching datasets: {e}")
            raise
