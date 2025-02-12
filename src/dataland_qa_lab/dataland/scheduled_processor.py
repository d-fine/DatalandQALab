import json
import logging
import os
import time

import requests

from dataland_qa_lab.database.database_engine import create_tables, get_entity
from dataland_qa_lab.database.database_tables import ReviewedDataset
from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets
from dataland_qa_lab.review.dataset_reviewer import review_dataset
from dataland_qa_lab.utils import console_logger

logger = logging.getLogger(__name__)
console_logger.configure_console_logger()

url = os.getenv("SLACK_WEBHOOK_URL")


def run_scheduled_processing(single_pass_e2e: bool = False) -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    logger.info("Creating database.")
    create_tables()
    while True:
        try:
            unreviewed_datasets = UnreviewedDatasets()
            list_of_data_ids = unreviewed_datasets.list_of_data_ids
            logger.info("Processing unreviewed datasets with the list of Data-IDs: %s", list_of_data_ids)

            for data_id in reversed(list_of_data_ids[:]):
                try:
                    existing_entity = None if single_pass_e2e else get_entity(data_id, ReviewedDataset)
                    if existing_entity is None:
                        message = f"🔍 Starting review of the Dataset with the Data-ID: {data_id}"
                        logger.info("Dataset with the Data-ID does not exist in the database. Starting review.")
                        send_alert_message(message=message)
                        review_dataset(data_id)
                        list_of_data_ids.remove(data_id)
                        message = f"✅ Review is successful for the dataset with the Data-ID: {data_id}"
                        send_alert_message(message=message)
                    else:
                        logger.info("Dataset with the Data-ID already exists in the database.")

                except Exception:
                    message = f"❗An error occured while reviewing the dataset with the Data-ID: {data_id}"
                    logger.exception("Error processing dataset with the Data-ID: %s", data_id)
                    send_alert_message(message=message)

            if single_pass_e2e:
                break
            time.sleep(10)
        except Exception as e:
            logger.critical("Critical error: %s", e)
            raise


def send_alert_message(message: str) -> None:
    """Sends an Alert Message to the Slackbot."""
    payload = {"text": message}

    headers = {"Content-Type": "application/json"}

    response = requests.post(url=url, data=json.dumps(payload), headers=headers)

    status = 200

    assert response.status_code == status
    assert response.text == "ok"
