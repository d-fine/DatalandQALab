import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from pydantic import BaseModel

from dataland_qa_lab.database.database_engine import create_tables
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.review.dataset_reviewer import review_dataset
from dataland_qa_lab.utils import console_logger


class ReviewRequest(BaseModel):
    """Request body for the /review/{data_id} POST endpoint."""

    ai_model: str = "gpt-4o"
    force_review: bool = False
    use_ocr: bool = True


class ReviewMeta(BaseModel):
    """Metadata about the review request and processing."""

    timestamp: datetime
    data_id: str
    ai_model: str
    force_review: bool
    use_ocr: bool


class ReviewResponse(BaseModel):
    """Response wrapper containing data and metadata."""

    data: dict[str, Any]
    meta: ReviewMeta


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


@dataland_qa_lab.get("/review/{data_id}")
def review_dataset_endpoint(data_id: str, force_review: bool = False) -> str:
    """Review a single dataset via API call."""
    report_data = review_dataset(data_id=data_id, force_review=force_review)
    return report_data


@dataland_qa_lab.post("/review/{data_id}", response_model=ReviewResponse)
def review_dataset_post_endpoint(data_id: str, body: ReviewRequest) -> ReviewResponse:
    """Review a single dataset via API call (configurable)."""
    report_id = review_dataset(
        data_id=data_id,
        force_review=body.force_review,
        ai_model=body.ai_model,
        use_ocr=body.use_ocr,
    )

    data: dict[str, Any] = {"report_id": report_id}

    meta = ReviewMeta(
        timestamp=datetime.now(timezone.UTC),
        data_id=data_id,
        ai_model=body.ai_model,
        force_review=body.force_review,
        use_ocr=body.use_ocr,
    )

    return ReviewResponse(data=data, meta=meta)
