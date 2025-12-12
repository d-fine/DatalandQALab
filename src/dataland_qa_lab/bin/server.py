import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException, status

from dataland_qa_lab.bin import models
from dataland_qa_lab.data_point_flow import models as datapoint_flow_models
from dataland_qa_lab.data_point_flow import review
from dataland_qa_lab.database.database_engine import create_tables, verify_database_connection
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.review import dataset_reviewer, exceptions
from dataland_qa_lab.utils import config, console_logger
from dataland_qa_lab.utils.datetime_helper import get_german_time_as_string

logger = logging.getLogger("dataland_qa_lab.bin.server")
config = config.get_config()


console_logger.configure_console_logger()
logger.info("Launching the Dataland QA Lab server")
verify_database_connection()
create_tables()

scheduler = BackgroundScheduler()
trigger = CronTrigger(minute="*/10")
# old scheduler
scheduler.add_job(scheduled_processor.old_run_scheduled_processing, trigger, next_run_time=datetime.now())  # noqa: DTZ005
# new scheduler
# scheduler.add_job(data_point_scheduler.run_scheduled_processing, trigger, next_run_time=datetime.now())
if not config.is_dev_environment:
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

    meta = models.ReviewMeta(
        timestamp=get_german_time_as_string(),
        ai_model=data.ai_model,
        force_review=data.force_review,
        use_ocr=data.use_ocr,
    )

    return models.ReviewResponse(data=report, meta=meta)


# new validation flow using datapoints


@dataland_qa_lab.post("/data-point-flow/review-data-point/{data_point_id}", response_model=None)
async def review_data_point_id(
    data_point_id: str,
    data: models.DatapointFlowReviewDataPointRequest,
) -> datapoint_flow_models.ValidatedDatapoint | datapoint_flow_models.CannotValidateDatapoint:
    """Review a single dataset via API call (configurable)."""
    try:
        return await review.validate_datapoint(
            data_point_id=data_point_id, ai_model=data.ai_model, use_ocr=data.use_ocr, override=data.override
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@dataland_qa_lab.post("/data-point-flow/review-dataset/{data_id}", response_model=None)
async def review_data_point_dataset_id(
    data_id: str,
    data: models.DatapointFlowReviewDataPointRequest,
) -> dict[str, datapoint_flow_models.ValidatedDatapoint | datapoint_flow_models.CannotValidateDatapoint] | str:
    """Review a single dataset via API call (configurable)."""
    try:
        data_points = config.dataland_client.meta_api.get_contained_data_points(data_id)

        tasks = {
            k: review.validate_datapoint(v, use_ocr=data.use_ocr, ai_model=data.ai_model, override=data.override)
            for k, v in data_points.items()
        }

        results_list = await asyncio.gather(*tasks.values())

        return dict(zip(tasks.keys(), results_list, strict=False))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
