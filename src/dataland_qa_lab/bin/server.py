import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from dataland_qa_lab.bin.models import ReviewMeta, ReviewResponse
from dataland_qa_lab.database.database_engine import create_tables
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.review.dataset_reviewer import review_dataset_via_api
from dataland_qa_lab.utils import console_logger
from dataland_qa_lab.utils.datetime_helper import get_german_time_as_string

logger = logging.getLogger("dataland_qa_lab.bin.server")

console_logger.configure_console_logger()
logger.info("Launching the Dataland QA Lab server")
create_tables()

scheduler = BackgroundScheduler()
trigger = CronTrigger(minute="*/10")
job = scheduler.add_job(scheduled_processor.run_scheduled_processing, trigger, next_run_time=datetime.now())  # noqa: DTZ005
scheduler.start()


@asynccontextmanager
async def lifespan(dataland_qa_lab: FastAPI):  # noqa: ANN201, ARG001, RUF029
    """Ensures that the scheduler shuts down correctly."""
    yield
    scheduler.shutdown()


dataland_qa_lab = FastAPI(lifespan=lifespan)


@dataland_qa_lab.post("/review/{data_id}", response_model=ReviewResponse)
def review_dataset_post_endpoint(
    data_id: str, force_review: bool = False, ai_model: str = "gpt-4o", use_ocr: bool = True
) -> ReviewResponse:
    """Review a single dataset via API call (configurable)."""
    # todo: use_ocr needs to be implemented still
    report = review_dataset_via_api(
        data_id=data_id,
        force_review=force_review,
        ai_model=ai_model,
        use_ocr=use_ocr,
    )

    meta = ReviewMeta(
        timestamp=get_german_time_as_string(),
        ai_model=ai_model,
        force_review=force_review,
        use_ocr=use_ocr,
    )

    return ReviewResponse(data=report, meta=meta)
