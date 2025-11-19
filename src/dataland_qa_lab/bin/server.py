import logging
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from dataland_qa_lab.database.database_engine import create_tables
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.review.dataset_reviewer import retrieve_dataset_from_dataland, review_dataset
from dataland_qa_lab.utils import console_logger

logger = logging.getLogger("dataland_qa_lab.bin.server")

console_logger.configure_console_logger()
logger.info("Launching the Dataland QA Lab server")
create_tables()

scheduler = BackgroundScheduler()
trigger = CronTrigger(minute="*/10")
job = scheduler.add_job(scheduled_processor.run_scheduled_processing, trigger, next_run_time=datetime.now())  # noqa: DTZ005
# scheduler.start()
# todo: enable scheduler again after testing


@asynccontextmanager
async def lifespan(dataland_qa_lab: FastAPI):  # noqa: ANN201, ARG001, RUF029
    """Ensures that the scheduler shuts down correctly."""
    yield
    scheduler.shutdown()


dataland_qa_lab = FastAPI(lifespan=lifespan)


@dataland_qa_lab.get("/review/{data_id}")
def review_dataset_endpoint(data_id: str, framework: str = "sfdr", force_review: bool = False) -> dict:
    """Review a single dataset via API call."""
    dataland_data = retrieve_dataset_from_dataland(data_id=data_id, framework=framework)
    if dataland_data is None:
        return {"error": "Dataset not found"}

    review_dataset(dataland_data, framework=framework)
    return "test"
