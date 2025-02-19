import logging
import time

from dataland_qa_lab.dataland.alerting import send_alert_message
from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets
from dataland_qa_lab.review.dataset_reviewer import review_dataset

logger = logging.getLogger(__name__)


def run_scheduled_processing(single_pass_e2e: bool = False) -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    try:
        unreviewed_datasets = UnreviewedDatasets()
        list_of_data_ids = unreviewed_datasets.list_of_data_ids
        logger.info("Processing unreviewed datasets with the list of Data-IDs: %s", list_of_data_ids)
        for data_id in reversed(list_of_data_ids[:]):
            try:
                review_dataset(data_id)
                list_of_data_ids.remove(data_id)
            except Exception:
                message = f"❗An error occured while reviewing the dataset with the Data-ID: {data_id}"
                logger.exception("Error processing dataset with the Data-ID: %s", data_id)
                send_alert_message(message=message)
        if single_pass_e2e:
            return
    except Exception as e:
        logger.critical("Critical error: %s", e)
        raise
