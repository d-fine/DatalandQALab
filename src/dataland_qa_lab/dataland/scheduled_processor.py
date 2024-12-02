import logging
import time

from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets


def run_scheduled_processing(iterations: int) -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    max_iterations = 10
    counter = 0
    while counter < iterations and counter < max_iterations:
        counter += 1
        try:
            unreviewed_datasets = UnreviewedDatasets()
            list_of_data_ids = unreviewed_datasets.list_of_data_ids

            if not list_of_data_ids:
                time.sleep(600)
                continue

            # Process datasets from end to start
            for data_id in reversed(list_of_data_ids[:]):
                try:
                    successfully_processed = True  # Replace logic with actual call of the revieweDataset
                    if successfully_processed:
                        list_of_data_ids.remove(data_id)

                except Exception:
                    logging.exception("Error processing dataset %s", data_id)

        except Exception as e:
            logging.critical("Critical error: %s", e)
            raise
