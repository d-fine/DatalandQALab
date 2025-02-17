import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from dataland_qa_lab.database.database_engine import create_tables
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.review.dataset_reviewer import review_dataset
from dataland_qa_lab.utils import console_logger

logger = logging.getLogger("dataland_qa_lab.bin.server")

scheduler = BackgroundScheduler()
trigger = CronTrigger(minute="10", start_date="in 5 Minutes")
scheduler.add_job(scheduled_processor.run_scheduled_processing(), trigger)
scheduler.start()


@asynccontextmanager
async def lifespan(dataland_qa_lab: FastAPI):
    """FastAPI starts first, then runs main()."""
    console_logger.configure_console_logger()
    logger.info("Launching the Dataland QA Lab server")
    create_tables()
    yield
    scheduler.shutdown()


dataland_qa_lab = FastAPI(lifespan=lifespan)


@dataland_qa_lab.get("/review/{data_id}")
def review_dataset_endpoint(data_id: str, force_review: bool = False) -> str:
    """Review a single dataset via API call."""
    report_data = review_dataset(data_id=data_id, force_review=force_review)
    return report_data.report_id
