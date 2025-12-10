import asyncio
import async_lru
import io
import json
import logging
import time
import functools

import pypdf
from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.database import database_engine, database_tables
from dataland_qa_lab.dataland import dataset_provider
from dataland_qa_lab.models import data_point_flow
from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.utils import ai, config, prompts, slack


config = config.get_config()


logger = logging.getLogger(__name__)
validation_prompts = prompts.get_prompts()


_lock_map = {}
_lock_map_lock = asyncio.Lock()


def get_lock_for(key):
    """Return a per-key lock, creating it if needed."""

    async def _get():
        async with _lock_map_lock:
            if key not in _lock_map:
                _lock_map[key] = asyncio.Lock()
            return _lock_map[key]

    return _get()


async def validate_datapoint(
    data_point_id: str, use_ocr: bool, ai_model: str, override: bool
) -> data_point_flow.ValidatedDatapoint | None:
    """Validates a datapoint given a data_point_id."""
    logger.info("Validating datapoint with ID: %s", data_point_id)

    try:
        data_point = await get_data_point(data_point_id)
    except Exception as e:
        return None

    prompt = get_prompt_config(data_point.data_point_type)

    if prompt:
        downloaded_document = await get_document(reference_id=data_point.file_reference, page_num=data_point.page)
        if use_ocr:
            ocr_text = await run_ocr_on_document(
                file_name=data_point.file_name,
                file_reference=data_point.file_reference,
                page=data_point.page,
                document=downloaded_document,
            )
            prompt_text = prompt.prompt.format(context=ocr_text)
            res = ai.execute_prompt(prompt=prompt_text, ai_model=ai_model)
        else:
            # implement images
            ocr_text = ""
            res = data_point_flow.AIResponse(predicted_answer=None, confidence=0.0, reasoning="OCR not used.")

        return data_point_flow.ValidatedDatapoint(
            data_point_id=data_point.data_point_id,
            data_point_type=data_point.data_point_type,
            previous_answer=data_point.value,
            predicted_answer=res.predicted_answer,
            confidence=res.confidence,
            reasoning=res.reasoning,
            qa_status=QaStatus.ACCEPTED if res.predicted_answer == data_point.value else QaStatus.REJECTED,
            timestamp=int(time.time()),
            ai_model=ai_model,
            use_ocr=use_ocr,
            file_name=data_point.file_name,
            file_reference=data_point.file_reference,
            page=data_point.page,
        )
        pass
    return None


@async_lru.alru_cache
async def get_data_point(data_point_id: str) -> data_point_flow.DataPoint:
    """Returns a DataPoint object for the given data_point_id and also validates its structure."""
    logger.info("Fetching data point with ID: %s", data_point_id)
    data_point = config.dataland_client.data_points_api.get_data_point(data_point_id)
    dp_json = json.loads(data_point.data_point)

    data_point_type = data_point.data_point_type
    if dp_json.get("dataSource") is None:
        msg = f"Data point {data_point_id} is missing dataSource information."
        raise ValueError(msg)
    page = int(dp_json["dataSource"].get("page", 0))
    file_reference = dp_json["dataSource"].get("fileReference", "")
    file_name = dp_json["dataSource"].get("fileName", "")
    value = dp_json.get("value", "")

    return data_point_flow.DataPoint(
        data_point_id=data_point_id,
        data_point_type=data_point_type,
        data_source=dp_json.get("dataSource", {}),
        page=page,
        file_reference=file_reference,
        file_name=file_name,
        value=value,
    )


@async_lru.alru_cache
async def get_document(reference_id: str, page_num: int) -> io.BytesIO:
    """Return a PDF document stream for specific pages."""
    logger.info("Downloading document with reference ID: %s", reference_id)
    full_pdf = config.dataland_client.documents_api.get_document(reference_id)
    full_pdf_stream = io.BytesIO(full_pdf)

    original_pdf = pypdf.PdfReader(full_pdf_stream)
    output_pdf = pypdf.PdfWriter()

    if 0 <= page_num - 1 < len(original_pdf.pages):
        output_pdf.add_page(original_pdf.pages[page_num - 1])

    extracted_pdf_stream = io.BytesIO()
    output_pdf.write(extracted_pdf_stream)
    extracted_pdf_stream.seek(0)

    return extracted_pdf_stream


@async_lru.alru_cache
async def run_ocr_on_document(file_name: str, file_reference: str, page: int, document: io.BytesIO) -> str:
    """Run OCR on the given PDF document and return the extracted text."""
    logger.info("Running OCR on document with reference ID: %s, page: %d", file_reference, page)

    key = (file_name, file_reference, page)
    lock = await get_lock_for(key)

    async with lock:
        cached_document = database_engine.get_entity(
            database_tables.CachedDocument, file_reference=file_reference, page=page
        )

        if cached_document:
            return cached_document.ocr_output

        markdown = text_to_doc_intelligence.extract_pdf(document)

        database_engine.add_entity(
            database_tables.CachedDocument(
                file_name=file_name,
                file_reference=file_reference,
                ocr_output=markdown,
                page=page,
            )
        )
        return markdown


def get_prompt_config(data_point_type: str) -> data_point_flow.DataPointPrompt | None:
    """Retrieve the validation prompt or raise an error if not found."""
    logger.info("Retrieving prompt for data point type: %s", data_point_type)
    if config.is_dev_environment:
        validation_prompts = prompts.get_prompts()

    prompt = validation_prompts.get(data_point_type)
    if prompt:
        return data_point_flow.DataPointPrompt(prompt=prompt.get("prompt"), depends_on=prompt.get("depends_on", []))

    logger.warning("No prompt found for data point type: %s. Skipping...", data_point_type)
    return None
