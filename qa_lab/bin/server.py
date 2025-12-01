import logging
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Path
from fastapi.concurrency import asynccontextmanager

from qa_lab.database import database_engine
from qa_lab.validator import scheduler, validator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("dataland_qa_lab.bin.server")

logger.info("Launching the Dataland QA Lab server")
database_engine.check_connection()
database_engine.create_tables()


fastapi_scheduler = BackgroundScheduler()
trigger = CronTrigger(minute="*/10")
job = fastapi_scheduler.add_job(scheduler.run_scheduled_processing, trigger, next_run_time=datetime.now())  # noqa: DTZ005
fastapi_scheduler.start()


@asynccontextmanager
async def lifespan(dataland_qa_lab: FastAPI):  # noqa: ANN201, ARG001, RUF029
    """Ensures that the scheduler shuts down correctly."""
    yield
    fastapi_scheduler.shutdown()


qa_lab = FastAPI(lifespan=lifespan)


@qa_lab.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "timestamp": int(time.time())}


@qa_lab.post("/review-data-point/{data_point_id}")
def review_data_point_id(
    data_point_id: str = Path(..., pattern=r"^[a-zA-Z0-9_-]+$"),
    ai_model: str = "gpt-4o",
    use_ocr: bool = True,
    override: bool = False,
) -> validator.ValidatedDatapoint | dict | None:
    """Review a single dataset via API call (configurable)."""
    # todo: use_ocr needs to be implemented still
    try:
        res = validator.validate_datapoint(
            data_point_id=data_point_id, ai_model=ai_model, use_ocr=use_ocr, override=override
        )
        if res:
            return res
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
