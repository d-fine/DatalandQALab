import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException, status

from dataland_qa_lab.bin import models
from dataland_qa_lab.data_point_flow import dataland, review
from dataland_qa_lab.data_point_flow import models as datapoint_flow_models
from dataland_qa_lab.data_point_flow import scheduler as data_point_scheduler
from dataland_qa_lab.database.database_engine import create_tables, verify_database_connection
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.review import dataset_reviewer, exceptions
from dataland_qa_lab.utils import config, console_logger
from dataland_qa_lab.utils.datetime_helper import get_german_time_as_string

console_logger.configure_console_logger()
logger = logging.getLogger("dataland_qa_lab.bin.server")
conf = config.get_config()

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(_: FastAPI):  # noqa: ANN201, RUF029
    """Ensures that the scheduler shuts down correctly."""
    logger.info("Launching the Dataland QA Lab server")

    verify_database_connection()
    create_tables()

    trigger = CronTrigger(minute="*/10")
    if conf.is_local_environment:
        logger.info("Local environment detected. Not starting any scheduler.")
    elif conf.is_dev_environment:
        logger.info("Development environment detected. Using new scheduler.")
        scheduler.add_job(
            data_point_scheduler.run_scheduled_processing,
            trigger,
            next_run_time=datetime.now(),  # noqa: DTZ005
        )
    else:
        logger.info("Production environment detected. Using old scheduler.")
        scheduler.add_job(
            scheduled_processor.old_run_scheduled_processing,
            trigger,
            next_run_time=datetime.now(),  # noqa: DTZ005
        )

    if scheduler.get_jobs():
        logger.info("Starting scheduler with %d jobs.", len(scheduler.get_jobs()))
        scheduler.start()

    yield

    if scheduler.running:
        logger.info("Shutting down scheduler.")
        scheduler.shutdown()


dataland_qa_lab = FastAPI(lifespan=lifespan)


@dataland_qa_lab.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "timestamp": get_german_time_as_string()}


@dataland_qa_lab.post("/review/{data_id}", response_model=models.ReviewResponse)
def review_dataset_post_endpoint(data_id: str, data: models.ReviewRequest) -> models.ReviewResponse:
    """Review a single dataset via API call (configurable)."""
    try:
        report = dataset_reviewer.old_review_dataset_via_api(
            data_id=data_id,
            force_review=data.force_review,
            ai_model=data.ai_model,
            use_ocr=data.use_ocr,
        )
    except exceptions.DatasetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (exceptions.OCRProcessingError, exceptions.DataCollectionError, exceptions.ReportSubmissionError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except exceptions.ReviewError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return models.ReviewResponse(
        data=report,
        meta=models.ReviewMeta(
            timestamp=get_german_time_as_string(),
            ai_model=data.ai_model,
            force_review=data.force_review,
            use_ocr=data.use_ocr,
        ),
    )


@dataland_qa_lab.post("/data-point-flow/review-data-point/{data_point_id}", response_model=None)
async def review_data_point_id(
    data_point_id: str,
    data: models.DatapointFlowReviewDataPointRequest,
) -> datapoint_flow_models.ValidatedDatapoint | datapoint_flow_models.CannotValidateDatapoint:
    """Review a single dataset via API call (configurable)."""
    return await review.validate_datapoint(
        data_point_id=data_point_id, ai_model=data.ai_model, use_ocr=data.use_ocr, override=data.override
    )


@dataland_qa_lab.post("/data-point-flow/review-dataset/{data_id}", response_model=None)
async def review_data_point_dataset_id(
    data_id: str,
    data: models.DatapointFlowReviewDataPointRequest,
) -> (
    dict[str, datapoint_flow_models.ValidatedDatapoint | datapoint_flow_models.CannotValidateDatapoint] | HTTPException
):
    """Review a single dataset via API call (configurable)."""
    try:
        data_points = await dataland.get_contained_data_points(data_id)
    except Exception as e:
        logger.exception("Failed to fetch data points for dataset %s", data_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error fetching data points from Dataland: {e}",
        ) from e

    keys = list(data_points.keys())
    tasks = [
        review.validate_datapoint(
            data_points[k], use_ocr=data.use_ocr, ai_model=data.ai_model, override=data.override, dataset_id=data_id
        )
        for k in keys
    ]

    results_list = await asyncio.gather(*tasks)
    return dict(zip(keys, results_list, strict=True))
