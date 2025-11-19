import logging
# from contextlib import asynccontextmanager
# from datetime import datetime

# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from dataland_qa_lab.categories.nuclear_and_gas_data.dataset_provider import get_nuclear_and_gas_dataset_by_id
from dataland_qa_lab.categories.nuclear_and_gas_data.reviewer import review_nuclear_and_gas_dataset
from dataland_qa_lab.categories.sfdr.dataset_provider import get_sfdr_dataset_by_id
from dataland_qa_lab.database.database_engine import create_tables

# from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.review.dataset_reviewer import retrieve_dataset_from_dataland
from dataland_qa_lab.utils import console_logger

logger = logging.getLogger("dataland_qa_lab.bin.server")

console_logger.configure_console_logger()
logger.info("Launching the Dataland QA Lab server")
create_tables()

# scheduler = BackgroundScheduler()
# trigger = CronTrigger(minute="*/10")
# job = scheduler.add_job(scheduled_processor.run_scheduled_processing, trigger, next_run_time=datetime.now())  # noqa: DTZ005
# scheduler.start()
# todo: enable scheduler again after testing


# @asynccontextmanager
# async def lifespan(dataland_qa_lab: FastAPI):  # noqa: ANN201, ARG001, RUF029
#   """Ensures that the scheduler shuts down correctly."""
#  yield
# scheduler.shutdown()


dataland_qa_lab = FastAPI()  # lifespan=lifespan)


@dataland_qa_lab.get("/review/{data_id}")
def review_dataset_endpoint(
    data_id: str, framework: str = "sfdr", force_override: bool = False, ai_model: str = "gpt-4", use_ocr: bool = True
) -> dict:
    """Review a single dataset via API call."""
    dataland_data = retrieve_dataset_from_dataland(data_id=data_id, framework=framework)
    if dataland_data is None:
        return {"error": "Dataset not found"}

    report = None

    match framework:
        case "nuclear-and-gas":
            dataset = get_nuclear_and_gas_dataset_by_id(data_id)
            if dataset is None:
                return {"error": "Dataset not found in Dataland"}
            report = review_nuclear_and_gas_dataset(data_id=data_id, dataset=dataset, force_override=force_override)
        case "sfdr":
            dataset = get_sfdr_dataset_by_id(data_id)

        case _:
            return {"error": "Unsupported framework"}

    if report:
        return {"data": report}

    return {"error": "Review failed"}
