from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets
import time

def run_scheduled_processing():
    while True:
        try:
            unreviewed_datasets = UnreviewedDatasets()
            list_of_data_ids = unreviewed_datasets.list_of_data_ids

            if not list_of_data_ids:
                time.sleep(600)
                continue

            # Process datasets from end to start
            for data_id in reversed(list_of_data_ids[:]):
                try:
                    successfully_processed = True # Replace logic with actual call of the revieweDataset
                    if successfully_processed:
                        list_of_data_ids.remove(data_id) 

                except Exception as e:
                    print(f"Error processing dataset {data_id}: {e}")

        except Exception as e:
            print(f"Critical error: {e}")
            break