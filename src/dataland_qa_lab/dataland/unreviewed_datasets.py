from dataland_qa_lab.utils import config


class UnreviewedDatasets:
    """Class to manage unreviewed datasets from the API."""
    
    # Klassenvariablen
    conf = config.get_config()
    dataland_client = conf.dataland_client

    def __init__(self):
        self.total_count = self.dataland_client.qa_api.get_number_of_pending_datasets()
        self.datasets = self.dataland_client.qa_api.get_info_on_pending_datasets(self.total_count)
        self.data_ids = [dataset["dataId"] for dataset in self.datasets]

    def update_datasets(self):
        self.total_count = self.dataland_client.qa_api.get_number_of_pending_datasets()
        self.datasets = self.dataland_client.qa_api.get_info_on_pending_datasets(self.total_count)
        self.data_ids = [dataset["dataId"] for dataset in self.datasets]

    def get_oldest_dataid(self):
        if self.data_ids:
            oldest_id = self.data_ids.pop(0)
            self.datasets.pop(0)
            return oldest_id
        else:
            return None

    def is_empty(self):
        return len(self.data_ids) == 0

