import asyncio
import logging
import time

from dataland_qa.models.qa_status import QaStatus
from sqlalchemy.exc import IntegrityError

from dataland_qa_lab.data_point_flow import review
from dataland_qa_lab.database import database_engine, database_tables
from dataland_qa_lab.utils import config, slack

logger = logging.getLogger(__name__)
config = config.get_config()
LOCK_TTL_SECONDS = 15 * 60  # 15 minutes


def try_acquire_lock(data_point_id: str) -> bool:
    """Returns True if the lock was acquired, False if datapoint should be skipped."""
    existing_lock = database_engine.get_entity(
        entity_class=database_tables.DatapointInReview,
        data_point_id=data_point_id,
    )

    if existing_lock:
        age = int(time.time()) - existing_lock.locked_at
        if age < LOCK_TTL_SECONDS:
            logger.info("Datapoint %s is already in review (age=%ss). Skipping.", data_point_id, age)
            return False

        logger.warning("Datapoint %s lock is stale (age=%ss). Proceeding to review.", data_point_id, age)
        database_engine.delete_entity(entity_id=data_point_id, entity_class=database_tables.DatapointInReview)
    try:
        database_engine.add_entity(
            database_tables.DatapointInReview(
                data_point_id=data_point_id,
            )
        )
    except IntegrityError:
        logger.info("Datapoint %s already being processed. Skipping.", data_point_id)
        return False
    else:
        return True


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
        inconclusive = []
        not_attempted = []

        for _k, v in data_points.items():  # noqa: PERF102
            if not try_acquire_lock(v):
                continue

            try:
                validator_result = asyncio.run(
                    review.validate_datapoint(
                        data_point_id=v,
                        ai_model=config.ai_model,
                        use_ocr=config.use_ocr,
                        override=False,
                    )
                )
            except Exception:
                logger.exception("Error occurred while validating datapoint ID: %s", v)
                not_attempted.append(v)
                continue
            finally:
                database_engine.delete_entity(entity_id=v, entity_class=database_tables.DatapointInReview)

            if isinstance(validator_result, review.models.ValidatedDatapoint):
                if validator_result.qa_status == "QaAccepted":
                    accepted_ids.append(validator_result.data_point_id)
                elif validator_result.qa_status == "QaRejected":
                    rejected_ids.append(validator_result.data_point_id)
                elif validator_result.qa_status == "QaInconclusive":
                    inconclusive.append(validator_result.data_point_id)
            if isinstance(validator_result, review.models.CannotValidateDatapoint):
                not_attempted.append(validator_result.data_point_id)

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
            f"Dataset ID: {dataset_id} processed. ✅ Accepted: {len(accepted_ids)}, ❌ Rejected: {len(rejected_ids)}, ⚠️ Inconclusive: {len(inconclusive)}, ⚠️ Not validated: {len(not_attempted)}"  # noqa: E501
        )
