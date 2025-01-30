import logging

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)


class UnreviewedDatasets:
    """Class representing the unreviewed datasets from the API."""

    datasets: list[any]
    list_of_data_ids: list[str]

    def __init__(self) -> None:
        """Initialize the unreviewed datasets with the data from the API."""
        client = config.get_config().dataland_client
        logger.info(msg="Initializing the unreviewed Datasets with the data from Dataland.")

        try:
            number_of_datasets = client.qa_api.get_number_of_pending_datasets()
            if number_of_datasets is None or number_of_datasets < 0:
                msg_p = "Recieved an invalid number of pending datasets."
                logger.error(msg=msg_p, exc_info=ValueError)
                raise ValueError(msg_p)  # noqa: TRY301

            self.datasets = client.qa_api.get_info_on_pending_datasets(
                data_types=["nuclear-and-gas"], chunk_size=number_of_datasets
            )

            self.list_of_data_ids = [dataset.data_id for dataset in self.datasets]

        except Exception:
            logger.exception(msg="An error occurred", exc_info=Exception)
            raise
