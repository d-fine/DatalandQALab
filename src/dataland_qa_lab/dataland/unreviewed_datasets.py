import logging

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)


class UnreviewedDatasets:
    """Class representing the unreviewed datasets from the API."""

    datasets: list[any]
    list_of_data_ids: list[str]

    def __init__(self) -> None:
        """Initialize the unreviewed datasets with the data from the API."""
        try:
            client = config.get_config().dataland_client
            if client is None:
                msg = "Client Setup failed in the configuration."
                raise ValueError(msg)  # noqa: TRY301
        except TimeoutError:
            logger.exception("Timeout occurred while fetching the number of datasets.")
            raise
        except Exception:
            logger.exception("Error while creating UnreviewedDatasets object.")
            raise

        try:
            number_of_datasets = client.qa_api.get_number_of_pending_datasets()
            if number_of_datasets is None or number_of_datasets < 0:
                msg = "Recieved an invalid number of pending datasets."
                raise ValueError(msg)  # noqa: TRY301
            self.datasets = client.qa_api.get_info_on_pending_datasets(
                data_types=["nuclear-and-gas"], chunk_size=number_of_datasets
            )

            self.list_of_data_ids = [dataset.data_id for dataset in self.datasets]

        except TimeoutError:
            logger.exception("Timeout occurred while initializing the unreviewed datasets.")
            raise
        except Exception:
            logger.exception("An error occurred while initializing the unreviewed datasets.")
            raise
