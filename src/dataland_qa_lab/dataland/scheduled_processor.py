import logging
import time

from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets
from dataland_qa_lab.review.dataset_reviewer import review_dataset

logger = logging.getLogger(__name__)


def run_scheduled_processing(iterations: int) -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    max_iterations = 100
    counter = 0

    while counter < iterations and counter < max_iterations:
        counter += 1
        try:
            unreviewed_datasets = UnreviewedDatasets()
            list_of_data_ids = unreviewed_datasets.list_of_data_ids
            try:
                unreviewed_datasets = UnreviewedDatasets()
                list_of_data_ids = unreviewed_datasets.list_of_data_ids
            except Exception as e:
                logger.exception("Error initializing UnreviewedDatasets: %s", e)  # noqa: TRY401
                time.sleep(600)
                continue

            # Skip processing if no datasets are available
            if not list_of_data_ids:
                logger.info("No unreviewed datasets found. Retrying in 10 minutes.")
                time.sleep(600)
                continue

            # Process each dataset
            for data_id in reversed(list_of_data_ids[:]):
                try:
                    review_dataset(data_id)
                    list_of_data_ids.remove(data_id)
                except Exception as e:
                    logger.exception("Error processing dataset %s: %s", data_id, e)  # noqa: TRY401

        except Exception as e:  # noqa: BLE001
            # Log critical error but allow the loop to continue
            logger.critical("Critical error in processing loop: %s", e)
            time.sleep(600)
            continue

    logger.info("Scheduled processing completed after %d iterations.", counter)
