import logging
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse

from dataland_qa_lab.bin.models import ReviewMeta, ReviewRequest, ReviewResponse
from dataland_qa_lab.database.database_engine import create_tables, verify_database_connection
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.review import dataset_reviewer
from dataland_qa_lab.utils import console_logger
from dataland_qa_lab.utils.datetime_helper import get_german_time_as_string

logger = logging.getLogger("dataland_qa_lab.bin.server")

console_logger.configure_console_logger()
logger.info("Launching the Dataland QA Lab server")
verify_database_connection()
create_tables()

scheduler = BackgroundScheduler()
trigger = CronTrigger(minute="*/10")
job = scheduler.add_job(scheduled_processor.old_run_scheduled_processing, trigger, next_run_time=datetime.now())  # noqa: DTZ005
scheduler.start()


@asynccontextmanager
async def lifespan(dataland_qa_lab: FastAPI):  # noqa: ANN201, ARG001, RUF029
    """Ensures that the scheduler shuts down correctly."""
    yield
    scheduler.shutdown()


dataland_qa_lab = FastAPI(lifespan=lifespan)


@dataland_qa_lab.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "timestamp": get_german_time_as_string()}


@dataland_qa_lab.post("/review/{data_id}", response_model=ReviewResponse)
def review_dataset_post_endpoint(data_id: str, data: ReviewRequest) -> ReviewResponse:
    """Review a single dataset via API call (configurable)."""
    # todo: use_ocr needs to be implemented still
    report = dataset_reviewer.old_review_dataset_via_api(
        data_id=data_id,
        force_review=data.force_review,
        ai_model=data.ai_model,
        use_ocr=data.use_ocr,
    )

    meta = ReviewMeta(
        timestamp=get_german_time_as_string(),
        ai_model=data.ai_model,
        force_review=data.force_review,
        use_ocr=data.use_ocr,
    )

    return ReviewResponse(data=report, meta=meta)


# new validation flow using datapoints


@dataland_qa_lab.post("/review-data-point/{data_point_id}")
def review_data_point_id(  # noqa: ANN201
    data_point_id: str,
    ai_model: str = "gpt-4o",
    use_ocr: bool = True,
    override: bool = False,
):
    """Review a single dataset via API call (configurable)."""
    # todo: use_ocr needs to be implemented still
    try:
        res = dataset_reviewer.validate_datapoint(
            data_point_id=data_point_id, ai_model=ai_model, use_ocr=use_ocr, override=override
        )
        if res:
            return JSONResponse(
                content={
                    "data_point_id": res.data_point_id,
                    "previous_answer": res.previous_answer,
                    "predicted_answer": res.predicted_answer,
                    "confidence": res.confidence,
                    "reasoning": res.reasoning,
                    "qa_status": res.qa_status,
                    "timestamp": res.timestamp,
                    "ai_model": res.ai_model,
                    "use_ocr": res.use_ocr,
                },
                status_code=200,
            )
    except Exception as e:  # noqa: BLE001
        return JSONResponse(content={"error": str(e)}, status_code=500)
