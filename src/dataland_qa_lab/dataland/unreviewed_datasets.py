from dataland_qa_lab.utils import config

class UnreviewedDatasets:
    """Class to manage unreviewed datasets from the API."""

    conf = config.get_config()
    dataland_client = conf.dataland_client

    def __init__(self):
        try:
            amount_of_datasets = self.dataland_client.qa_api.get_number_of_pending_datasets()
            if amount_of_datasets is None or amount_of_datasets < 0:
                raise ValueError("Received an invalid number of pending datasets.")

            self.datasets = self.dataland_client.qa_api.get_info_on_pending_datasets(
                data_types=["nuclear-and-gas"], chunk_size=amount_of_datasets
            )
            self.list_of_data_ids = [dataset.data_id for dataset in self.datasets]

        except Exception as e:
            print(f"Error fetching datasets: {e}")
            raise  # Propagate the error