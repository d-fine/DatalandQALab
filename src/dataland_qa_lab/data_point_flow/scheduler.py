import asyncio
import logging
import time
from collections.abc import Generator
from contextlib import contextmanager

from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import review
from dataland_qa_lab.database import database_engine, database_tables
from dataland_qa_lab.utils import config, slack

logger = logging.getLogger(__name__)
conf = config.get_config()

lock_ttl_seconds = 15 * 60
validation_timeout_seconds = 5 * 60


@contextmanager
def datapoint_lock(dp_id: str) -> Generator[bool, None, None]:
    """Context manager to handle lock acquisition and automatic release."""
    existing = database_engine.get_entity(database_tables.DatapointInReview, data_point_id=dp_id)

    if existing:
        age = int(time.time()) - existing.locked_at
        if age < lock_ttl_seconds:
            logger.info("Datapoint %s locked (age=%ss). Skipping.", dp_id, age)
            yield False
            return
        logger.warning("Datapoint %s lock stale. Overriding.", dp_id)

    if not database_engine.acquire_or_refresh_datapoint_lock(dp_id, lock_ttl_seconds):
        yield False
        return

    try:
        yield True
    finally:
        if not database_engine.delete_entity(dp_id, database_tables.DatapointInReview):
            logger.warning("Failed to release lock for %s.", dp_id)


async def process_dataset(dataset_id: str):
    """Handles the validation logic for a single dataset."""
    start_time = time.time()
    data_points = conf.dataland_client.meta_api.get_contained_data_points(dataset_id)

    stats = {"QaAccepted": 0, "QaRejected": 0, "QaInconclusive": 0, "Error": 0}

    for dp_id in data_points.values():
        with datapoint_lock(dp_id) as acquired:
            if not acquired:
                continue

            try:
                result = await asyncio.wait_for(
                    review.validate_datapoint(dp_id, ai_model=conf.ai_model, use_ocr=conf.use_ocr, override=False),
                    timeout=validation_timeout_seconds,
                )

                if isinstance(result, review.models.ValidatedDatapoint):
                    stats[result.qa_status] = stats.get(result.qa_status, 0) + 1
                else:
                    stats["Error"] += 1

            except (TimeoutError, Exception) as e:
                logger.exception("Failed to validate %s: %s", dp_id, e)
                stats["Error"] += 1

    database_engine.add_entity(
        database_tables.ReviewedDataset(
            data_id=dataset_id,
            review_start_time=str(int(start_time)),
            review_end_time=str(int(time.time())),
            review_completed=True,
        )
    )

    slack.send_slack_message(
        f"Dataset {dataset_id} processed.\n"
        f"✅ {stats['QaAccepted']} | ❌ {stats['QaRejected']} | "
        f"⚠️ {stats['QaInconclusive']} | 🚫 {stats['Error']}"
    )


def run_scheduled_processing() -> None:
    """Main entry point for the scheduled sync."""
    logger.info("Scheduled processing started.")

    pending_count = conf.dataland_client.qa_api.get_number_of_pending_datasets()
    datasets = conf.dataland_client.qa_api.get_info_on_datasets(
        qa_status=QaStatus.PENDING, chunk_size=pending_count, data_types=["sfdr"]
    )

    for ds in reversed(datasets):
        if database_engine.get_entity(database_tables.ReviewedDataset, data_id=ds.data_id):
            continue

        logger.info("Processing dataset: %s", ds.data_id)
        asyncio.run(process_dataset(ds.data_id))
