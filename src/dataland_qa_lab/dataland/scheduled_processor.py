import logging

from dataland_qa_lab.dataland.alerting import send_alert_message
from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets
from dataland_qa_lab.review.dataset_reviewer import review_dataset

logger = logging.getLogger(__name__)


def run_scheduled_processing() -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    try:
        unreviewed_datasets = UnreviewedDatasets()
        processing_queue = unreviewed_datasets.processing_queue
        if len(processing_queue) > 0:
            logger.info("Processing unreviewed datasets with the list of Data-IDs: %s", processing_queue)
            for item in reversed(processing_queue[:]):
                data_id = item["id"]
                framework = item["type"]
                try:
                    review_dataset(data_id=data_id, framework=framework)
                    processing_queue.remove(item)
                except Exception:
                    message = f"❗An error occured while reviewing the dataset with the Data-ID: {data_id}"
                    logger.exception("Error processing dataset with the Data-ID: %s", data_id)
                    send_alert_message(message=message)
        else:
            logger.info("No datasets to review.")
            return
    except Exception as e:
        logger.critical("Critical error: %s", e)
        raise
