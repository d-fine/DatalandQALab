import logging
import time

from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets
from dataland_qa_lab.review.dataset_reviewer import review_dataset


def run_scheduled_processing(iterations: int) -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    max_iterations = 100
    counter = 0
    while counter < iterations and counter < max_iterations:
        counter += 1
        try:
            unreviewed_datasets = UnreviewedDatasets()
            list_of_data_ids = unreviewed_datasets.list_of_data_ids

            if not list_of_data_ids:
                time.sleep(600)
                continue

            for data_id in reversed(list_of_data_ids[:]):
                try:
                    review_dataset(data_id)
                    list_of_data_ids.remove(data_id)

                except Exception:
                    logging.exception("Error processing dataset %s", data_id)

        except Exception as e:
            logging.critical("Critical error: %s", e)
            raise
