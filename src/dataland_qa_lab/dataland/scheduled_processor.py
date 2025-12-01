import logging
from collections import Counter

from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets
from dataland_qa_lab.review import dataset_reviewer
from dataland_qa_lab.utils import config, slack

from dataland_qa_lab.database import database_engine, database_tables

logger = logging.getLogger(__name__)
config = config.get_config()


def old_run_scheduled_processing() -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    try:
        unreviewed_datasets = UnreviewedDatasets()
        list_of_data_ids = unreviewed_datasets.list_of_data_ids
        if len(list_of_data_ids) > 0:
            logger.info("Processing unreviewed datasets with the list of Data-IDs: %s", list_of_data_ids)
            for data_id in reversed(list_of_data_ids[:]):
                try:
                    dataset_reviewer.old_review_dataset(data_id)
                    list_of_data_ids.remove(data_id)
                except Exception:
                    message = f"❗An error occured while reviewing the dataset with the Data-ID: {data_id}"
                    logger.exception("Error processing dataset with the Data-ID: %s", data_id)
                    slack.send_slack_message(message=message)
        else:
            logger.info("No datasets to review.")
            return
    except Exception as e:
        logger.critical("Critical error: %s", e)
        raise


def run_scheduled_processing() -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    logger.info("Scheduled processing started.")
    slack_message = []
    unreviewed_datasets = config.dataland_client.qa_api.get_info_on_datasets(
        qa_status=QaStatus.PENDING, chunk_size=2, data_types=config.frameworks_list
    )

    logger.info("Found %d unreviewed datasets. Starting processing.", len(unreviewed_datasets))
    for dataset in unreviewed_datasets:
        slack_message.append(f"⏳ Starting validation for dataset ID: {dataset.data_id}")
        logger.info("Processing dataset ID: %s", dataset.data_id)
        data_points = config.dataland_client.meta_api.get_contained_data_points(dataset.data_id)

        qa_status = Counter()

        for k, v in data_points.items():
            if not database_engine.get_entity(
                database_tables.ValidatedDataPoint,
            ):
                logger.info("Validating of type %s data point ID: %s", k, v)
                try:
                    validator_response = dataset_reviewer.validate_datapoint(
                        v, ai_model=config.ai_model, use_ocr=config.use_ocr, override=True
                    )
                    if validator_response.qa_status is QaStatus.ACCEPTED:
                        slack_message.append(f"✅ Data point ID: {v} (of type {k}) accepted.")
                        logger.info("Data point ID: %s accepted.", v)
                    else:
                        slack_message.append(f"❌ Data point ID: {v} (of type {k}) rejected.")
                        logger.info("Data point ID: %s rejected.", v)
                    qa_status[validator_response.qa_status] += 1
                    database_engine.add_entity(
                        database_tables.ValidatedDataPoint(
                            data_point_id=v,
                            qa_status=validator_response.qa_status,
                        )
                    )
                except Exception:
                    slack_message.append(
                        f"🟡 Couldn't find a verdict for data point ID: {v} (of type {k}). Maybe it's not yet implemented?"
                    )
                    logger.exception("Error processing data point ID %s", v)
                    qa_status[QaStatus.PENDING] += 1
                    database_engine.add_entity(
                        database_tables.ValidatedDataPoint(
                            data_point_id=v,
                            qa_status=QaStatus.PENDING,
                        )
                    )

        if qa_status[QaStatus.ACCEPTED] == len(data_points):
            logger.info("All data points accepted for dataset ID: %s", dataset.data_id)
            config.dataland_client.qa_api.change_qa_status(
                data_id=dataset.data_id, qa_status=QaStatus.ACCEPTED, overwrite_data_point_qa_status=False
            )
            slack_message.append(f"🎉 Dataset ID: {dataset.data_id} accepted with all data points.")
        else:
            logger.info(
                "Dataset ID: %s has %d Accepted, %d Rejected data points. Marking as Rejected.",
                dataset.data_id,
                qa_status[QaStatus.ACCEPTED],
                qa_status[QaStatus.REJECTED],
            )

            config.dataland_client.qa_api.change_qa_status(
                data_id=dataset.data_id, qa_status=QaStatus.REJECTED, overwrite_data_point_qa_status=False
            )
            slack_message.append(
                f"⚠️ Dataset ID: {dataset.data_id} rejected with "
                f"{qa_status[QaStatus.ACCEPTED]} accepted and {qa_status[QaStatus.REJECTED]} rejected out of {len(data_points)} data points."  # noqa: E501
            )
    if slack_message:
        slack.send_slack_message("\n".join(slack_message))
