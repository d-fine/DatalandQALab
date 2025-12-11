import asyncio
import io
import json
import logging
import time

import async_lru
import pypdf
from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import ai, models, ocr
from dataland_qa_lab.database import database_engine, database_tables
from dataland_qa_lab.utils import config, prompts

config = config.get_config()


logger = logging.getLogger(__name__)
validation_prompts = prompts.get_prompts()


_lock_map = {}
_lock_map_lock = asyncio.Lock()


def get_lock_for(key: str):  # noqa: ANN201
    """Return a per-key lock, creating it if needed."""

    async def _get():
        async with _lock_map_lock:
            if key not in _lock_map:
                _lock_map[key] = asyncio.Lock()
            return _lock_map[key]

    return _get()


async def validate_datapoint(
    data_point_id: str, use_ocr: bool, ai_model: str, override: bool
) -> models.ValidatedDatapoint | models.CannotValidateDatapoint:
    """Validates a datapoint given a data_point_id."""
    logger.info("Validating datapoint with ID: %s", data_point_id)

    try:
        data_point = await get_data_point(data_point_id)
    except Exception as e:  # noqa: BLE001
        return models.CannotValidateDatapoint(
            data_point_id=data_point_id,
            data_point_type=None,
            reasoning="Couldn't fetch data point: " + str(e),
            ai_model=ai_model,
            use_ocr=use_ocr,
            override=override,
            timestamp=int(time.time()),
        )

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
            res = await ai.execute_prompt(prompt=prompt_text, ai_model=ai_model)
        else:
            # implement images
            ocr_text = ""
            res = models.AIResponse(predicted_answer=None, confidence=0.0, reasoning="OCR not used.")

        qa_status = QaStatus.ACCEPTED if res.predicted_answer == data_point.value else QaStatus.REJECTED

        await override_dataland_qa(data_point_id=data_point.data_point_id, reasoning=res.reasoning, qa_status=qa_status)

        return models.ValidatedDatapoint(
            data_point_id=data_point.data_point_id,
            data_point_type=data_point.data_point_type,
            previous_answer=data_point.value,
            predicted_answer=res.predicted_answer,
            confidence=res.confidence,
            reasoning=res.reasoning,
            qa_status=qa_status,
            timestamp=int(time.time()),
            ai_model=ai_model,
            use_ocr=use_ocr,
            file_name=data_point.file_name,
            file_reference=data_point.file_reference,
            page=data_point.page,
            override=override,
        )
    return models.CannotValidateDatapoint(
        data_point_id=data_point.data_point_id,
        data_point_type=data_point.data_point_type,
        reasoning="No Prompt configured for this data point type.",
        ai_model=ai_model,
        use_ocr=use_ocr,
        timestamp=int(time.time()),
        override=override,
    )


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

    return models.DataPoint(
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

        markdown = ocr.extract_pdf(document)

        database_engine.add_entity(
            database_tables.CachedDocument(
                file_name=file_name,
                file_reference=file_reference,
                ocr_output=markdown,
                page=page,
            )
        )
        return markdown


def get_prompt_config(data_point_type: str) -> models.DataPointPrompt | None:
    """Retrieve the validation prompt or raise an error if not found."""
    logger.info("Retrieving prompt for data point type: %s", data_point_type)
    if config.is_dev_environment:
        validation_prompts = prompts.get_prompts()

    prompt = validation_prompts.get(data_point_type)
    if prompt:
        return models.DataPointPrompt(prompt=prompt.get("prompt"), depends_on=prompt.get("depends_on", []))

    logger.warning("No prompt found for data point type: %s. Skipping...", data_point_type)
    return None


async def override_dataland_qa(data_point_id: str, reasoning: str, qa_status: QaStatus) -> None:
    """Override Dataland QA status for the given data point ID."""
    logger.info("Overriding Dataland QA status for data point ID: %s to %s", data_point_id, qa_status)
    await asyncio.to_thread(
        config.dataland_client.qa_api.change_data_point_qa_status,
        data_point_id=data_point_id,
        qa_status=qa_status,
        comment=reasoning,
    )
