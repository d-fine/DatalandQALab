import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from dataland_qa_lab.database.database_engine import create_tables
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.review.dataset_reviewer import review_dataset
from dataland_qa_lab.utils import console_logger

logger = logging.getLogger("dataland_qa_lab.bin.server")


async def main(single_pass_e2e: bool = False) -> None:
    """Launch the QA Lab server."""
    console_logger.configure_console_logger()
    logger.info("Launching the Dataland QA Lab server")
    create_tables()
    asyncio.create_task(  # noqa: RUF006
        scheduled_processor.run_scheduled_processing(single_pass_e2e=single_pass_e2e)
    )


@asynccontextmanager
async def lifespan(dataland_qa_lab: FastAPI):
    """FastAPI starts first, then runs main()."""
    asyncio.create_task(main())
    yield  # 🚀 FastAPI fully starts here


dataland_qa_lab = FastAPI(lifespan=lifespan) # add lifespan maybe


@dataland_qa_lab.get("/review/{data_id}")
def review_dataset_endpoint(data_id: str, force_review: bool = False) -> str:
    """Review a single dataset via API call."""
    report_data = review_dataset(data_id=data_id, force_review=force_review)
    return report_data.report_id
