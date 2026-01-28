import asyncio
import logging
import time

from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import review
from dataland_qa_lab.database import database_engine, database_tables
from dataland_qa_lab.utils import config, slack

logger = logging.getLogger(__name__)
config = config.get_config()


def run_scheduled_processing() -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    logger.info("Scheduled processing started.")

    number_of_pending_datasets = config.dataland_client.qa_api.get_number_of_pending_datasets()

    unreviewed_datasets = config.dataland_client.qa_api.get_info_on_datasets(
        qa_status=QaStatus.PENDING, chunk_size=number_of_pending_datasets, data_types=["sfdr"]
    )

    dataset_ids = [i.data_id for i in unreviewed_datasets]

    if len(unreviewed_datasets) > 0:
        logger.info("Found %d unreviewed datasets. Starting processing.", len(unreviewed_datasets))

    for dataset_id in reversed(dataset_ids):
        start_time = int(time.time())
        if database_engine.get_entity(database_tables.ReviewedDataset, data_id=dataset_id):
            logger.info("Dataset ID: %s has already been processed. Skipping.", dataset_id)
            continue

        logger.info("Processing dataset ID: %s", dataset_id)
        data_points = config.dataland_client.meta_api.get_contained_data_points(dataset_id)

        accepted_ids = []
        rejected_ids = []
        not_validated_ids = []

        for _k, v in data_points.items():  # noqa: PERF102
            validator_result = asyncio.run(
                review.validate_datapoint(
                    data_point_id=v,
                    ai_model=config.ai_model,
                    use_ocr=config.use_ocr,
                    override=False,
                )
            )

            if isinstance(validator_result, review.models.ValidatedDatapoint):
                if validator_result.qa_status == QaStatus.ACCEPTED:
                    accepted_ids.append(validator_result.data_point_id)
                elif validator_result.qa_status == QaStatus.REJECTED:
                    rejected_ids.append(validator_result.data_point_id)
            if isinstance(validator_result, review.models.CannotValidateDatapoint):
                not_validated_ids.append(validator_result.data_point_id)
        database_engine.add_entity(
            database_tables.ReviewedDataset(
                data_id=dataset_id,
                review_start_time=str(start_time),
                review_end_time=str(time.time()),
                review_completed=True,
                report_id=None,
            )
        )

        slack.send_slack_message(
            f"Dataset ID: {dataset_id} processed. ✅ Accepted: {len(accepted_ids)}, ❌ Rejected: {len(rejected_ids)}, ⚠️ Not validated: {len(not_validated_ids)}"  # noqa: E501
        )
