from dataland_qa_lab.dataland.error_handling import ErrorHandling, DuplicateIDError, NetworkError, UnknownError
from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets
import time

def schedule_processing():
    while True:
        try:
            unreviewed_datasets = UnreviewedDatasets()

            if len (unreviewed_datasets.list_of_data_ids) == 0:
                time.sleep(600)
                continue

            for data_id in reversed(unreviewed_datasets.list_of_data_ids):
                try:
                    successfully_processed = True  # Replace with reviewDataset(data_id)
                    if successfully_processed:
                        unreviewed_datasets.list_of_data_ids.remove(data_id)

                except Exception as e:
                    print(f"Error processing dataset {data_id}: {e}")

        except Exception as e:
            print(f"Critical error: {e}")
            break
        
