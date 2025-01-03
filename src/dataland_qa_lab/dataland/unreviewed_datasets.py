import logging

from dataland_qa_lab.utils import config


class UnreviewedDatasets:
    """Class representing the unreviewed datasets from the API."""

    datasets: list[any]
    list_of_data_ids: list[str]

    def __init__(self) -> None:
        """Initialize the unreviewed datasets with the data from the API."""
        client = config.get_config().dataland_client

        try:
            number_of_datasets = client.qa_api.get_number_of_pending_datasets()
            if number_of_datasets is None or number_of_datasets < 0:
                msg = "Received an invalid number of pending datasets."
                raise ValueError(msg)  # noqa: TRY301

            self.datasets = client.qa_api.get_info_on_pending_datasets(
                data_types=["nuclear-and-gas"], chunk_size=number_of_datasets
            )

            self.list_of_data_ids = [dataset.data_id for dataset in self.datasets]

        except Exception:
            logging.exception("An error occurred")
            raise
