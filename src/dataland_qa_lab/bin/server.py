import logging
import time

from fastapi import FastAPI
from starlette.background import BackgroundTasks

from dataland_qa_lab.database.database_engine import create_tables
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.review.dataset_reviewer import review_dataset
from dataland_qa_lab.utils import console_logger

logger = logging.getLogger("dataland_qa_lab.bin.server")


def main(single_pass_e2e: bool = False) -> None:
    """Launch the QA Lab server."""
    logger.info("Launching the Dataland QA Lab server")
    console_logger.configure_console_logger()
    create_tables()

    scheduled_processor.run_scheduled_processing(single_pass_e2e=single_pass_e2e)

    while True:
        logger.info("Still running")
        if single_pass_e2e:
            break
        time.sleep(30)


dataland_qa_lab = FastAPI(title="FastAPI")


@dataland_qa_lab.on_event("startup")
async def startup_event() -> None:
    """Ensure start of main after startup."""
    background_tasks = BackgroundTasks()
    background_tasks.add_task(main)
    await background_tasks()

@dataland_qa_lab.get("/review/{data_id}")
def review_dataset_endpoint(data_id: str, force_review: bool = False) -> str:
    """Review a single dataset via API call."""
    report_data = review_dataset(data_id=data_id, force_review=force_review)
    return report_data.report_id
