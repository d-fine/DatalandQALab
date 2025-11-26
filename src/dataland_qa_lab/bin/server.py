import logging
import time

from fastapi import FastAPI

from dataland_qa_lab.database.database_engine import create_tables
from dataland_qa_lab.validator.validator import validate_datapoint

logger = logging.getLogger("dataland_qa_lab.bin.server")

logger.info("Launching the Dataland QA Lab server")
create_tables()


dataland_qa_lab = FastAPI()


@dataland_qa_lab.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "timestamp": int(time.time())}


@dataland_qa_lab.post("/review-datapoint/{data_point_id}")
def review_data_point_id(data_point_id: str, ai_model: str, use_ocr: bool = True) -> dict:
    """Review a single dataset via API call (configurable)."""
    # todo: use_ocr needs to be implemented still
    res = validate_datapoint(data_point_id=data_point_id, ai_model=ai_model, use_ocr=use_ocr)
    return res
