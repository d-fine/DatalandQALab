import asyncio
import io
import json
import logging

import async_lru
from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import models, prompts
from dataland_qa_lab.utils import config
from dataland_qa_lab.data_point_flow.pdf_handler import extract_single_page

config = config.get_config()


logger = logging.getLogger(__name__)
validation_prompts = prompts.get_prompts()


@async_lru.alru_cache
async def get_data_point(data_point_id: str) -> models.DataPoint:
    """Returns a DataPoint object for the given data_point_id and also validates its structure."""
    logger.info("Fetching data point with ID: %s", data_point_id)
    data_point = await asyncio.to_thread(
        config.dataland_client.data_points_api.get_data_point, data_point_id=data_point_id
    )
    dp_json = json.loads(data_point.data_point)

    data_point_type = data_point.data_point_type
    if dp_json.get("dataSource") is None:
        msg = f"Data point {data_point_id} is missing dataSource information."
        raise ValueError(msg)
    page = int(dp_json["dataSource"].get("page", 0))
    file_reference = dp_json["dataSource"].get("fileReference", "")
    file_name = dp_json["dataSource"].get("fileName", "")
    value = dp_json.get("value", "")
    comment = dp_json.get("comment", "")
    quality = dp_json.get("quality", "")

    return models.DataPoint(
        data_point_id=data_point_id,
        data_point_type=data_point_type,
        data_source=dp_json.get("dataSource", {}),
        page=page,
        file_reference=file_reference,
        file_name=file_name,
        value=value,
        comment=comment,
        quality=quality,
        _all=dp_json,
    )


@async_lru.alru_cache
async def get_document(reference_id: str, page_num: int) -> io.BytesIO:
    """Return a PDF document stream for specific pages."""
    logger.info("Downloading document with reference ID: %s", reference_id)
    full_pdf_bytes = await asyncio.to_thread(
        config.dataland_client.documents_api.get_document, document_id=reference_id
    )

    extracted_pdf_stream = await asyncio.to_thread(
        extract_single_page, full_pdf_bytes=full_pdf_bytes, page_number=page_num
    )
    return extracted_pdf_stream


async def override_dataland_qa(data_point_id: str, reasoning: str, qa_status: QaStatus) -> None:
    """Override Dataland QA status for the given data point ID."""
    logger.info("Overriding Dataland QA status for data point ID: %s to %s", data_point_id, qa_status)
    await asyncio.to_thread(
        config.dataland_client.qa_api.change_data_point_qa_status,
        data_point_id=data_point_id,
        qa_status=qa_status,
        comment=reasoning,
    )


@async_lru.alru_cache
async def get_contained_data_points(dataset_id: str) -> dict[str, str]:
    """Get all data point IDs contained in a dataset."""
    logger.info("Fetching data points contained in dataset ID: %s", dataset_id)
    return await asyncio.to_thread(config.dataland_client.meta_api.get_contained_data_points, data_id=dataset_id)
