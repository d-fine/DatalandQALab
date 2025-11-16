import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from dataland_qa_lab.database.database_engine import create_tables
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.review.dataset_reviewer import review_dataset_via_api
from dataland_qa_lab.utils import console_logger

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
def review_dataset_endpoint(
    data_id: str, force_override: bool = False, use_ocr: bool = False, ai_model: str = "gpt-4"
) -> dict:
    """Review a single dataset via API call."""
    start_time = int(time.time())
    report_data = review_dataset_via_api(data_id=data_id, force_override=force_override)
    end_time = int(time.time())
    return {
        "report_data": report_data,
        "start_time": start_time,
        "end_time": end_time,
        "force_override": force_override,
        "use_ocr": use_ocr,
        "ai_model": ai_model,
    }


@dataland_qa_lab.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}
