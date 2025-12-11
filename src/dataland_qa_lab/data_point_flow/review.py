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

    already_checked_data_point = await check_if_already_validated(data_point_id)
    if already_checked_data_point:
        if override:
            await delete_existing_entry(data_point_id)
        else:
            return already_checked_data_point

    try:
        data_point = await get_data_point(data_point_id)
    except Exception as e:  # noqa: BLE001
        res = models.CannotValidateDatapoint(
            data_point_id=data_point_id,
            data_point_type=None,
            reasoning="Couldn't fetch data point: " + str(e),
            ai_model=ai_model,
            use_ocr=use_ocr,
            override=override,
            timestamp=int(time.time()),
        )
        await store_data_point_in_db(res)
        return res

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
            already_checked_data_point = await ai.execute_prompt(prompt=prompt_text, ai_model=ai_model)
        else:
            # implement images
            ocr_text = ""
            already_checked_data_point = models.AIResponse(
                predicted_answer=None, confidence=0.0, reasoning="OCR not used."
            )

        qa_status = (
            QaStatus.ACCEPTED if already_checked_data_point.predicted_answer == data_point.value else QaStatus.REJECTED
        )

        await override_dataland_qa(
            data_point_id=data_point.data_point_id, reasoning=already_checked_data_point.reasoning, qa_status=qa_status
        )

        res = models.ValidatedDatapoint(
            data_point_id=data_point.data_point_id,
            data_point_type=data_point.data_point_type,
            previous_answer=data_point.value,
            predicted_answer=already_checked_data_point.predicted_answer,
            confidence=already_checked_data_point.confidence,
            reasoning=already_checked_data_point.reasoning,
            qa_status=qa_status,
            timestamp=int(time.time()),
            ai_model=ai_model,
            use_ocr=use_ocr,
            file_name=data_point.file_name,
            file_reference=data_point.file_reference,
            page=data_point.page,
            override=override,
        )
        await store_data_point_in_db(res)
        return res

    res = models.CannotValidateDatapoint(
        data_point_id=data_point.data_point_id,
        data_point_type=data_point.data_point_type,
        reasoning="No Prompt configured for this data point type.",
        ai_model=ai_model,
        use_ocr=use_ocr,
        timestamp=int(time.time()),
        override=override,
    )
    await store_data_point_in_db(res)
    return res


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
    full_pdf = await asyncio.to_thread(config.dataland_client.documents_api.get_document, document_id=reference_id)
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


async def store_data_point_in_db(data: models.ValidatedDatapoint | models.CannotValidateDatapoint) -> None:
    """Store the validated data point in the database."""
    logger.info("Storing validated data point ID: %s in the database.", data.data_point_id)
    if isinstance(data, models.CannotValidateDatapoint):
        await asyncio.to_thread(
            database_engine.add_entity,
            database_tables.ValidatedDataPoint(
                data_point_id=data.data_point_id,
                data_point_type=data.data_point_type,
                previous_answer=None,
                predicted_answer=None,
                confidence=0.0,
                reasoning=data.reasoning,
                qa_status=QaStatus.PENDING,
                timestamp=int(time.time()),
                ai_model=data.ai_model,
                use_ocr=data.use_ocr,
                file_reference=None,
                file_name=None,
                page=None,
            ),
        )
    else:
        await asyncio.to_thread(
            database_engine.add_entity,
            entity=database_tables.ValidatedDataPoint(
                data_point_id=data.data_point_id,
                data_point_type=data.data_point_type,
                previous_answer=data.previous_answer,
                predicted_answer=data.predicted_answer,
                confidence=data.confidence,
                reasoning=data.reasoning,
                qa_status=data.qa_status,
                timestamp=data.timestamp,
                ai_model=data.ai_model,
                use_ocr=data.use_ocr,
                file_reference=data.file_reference,
                file_name=data.file_name,
                page=data.page,
            ),
        )


async def check_if_already_validated(
    data_point_id: str,
) -> models.CannotValidateDatapoint | models.ValidatedDatapoint | None:
    """Check if the data point has already been validated."""
    existing_validation = await asyncio.to_thread(
        database_engine.get_entity,
        entity_class=database_tables.ValidatedDataPoint,
        data_point_id=data_point_id,
    )
    if not existing_validation:
        return None
    logger.info("Data point ID: %s has already been validated.", data_point_id)
    if existing_validation.predicted_answer is None:
        return models.CannotValidateDatapoint(
            data_point_id=data_point_id,
            data_point_type=existing_validation.data_point_type or None,
            reasoning=existing_validation.reasoning,
            ai_model=existing_validation.ai_model,
            use_ocr=existing_validation.use_ocr,
            override=None,
            timestamp=existing_validation.timestamp,
        )
    return models.ValidatedDatapoint(
        data_point_id=existing_validation.data_point_id,
        data_point_type=existing_validation.data_point_type,
        previous_answer=existing_validation.previous_answer,
        predicted_answer=existing_validation.predicted_answer,
        confidence=existing_validation.confidence,
        reasoning=existing_validation.reasoning,
        qa_status=existing_validation.qa_status,
        timestamp=existing_validation.timestamp,
        ai_model=existing_validation.ai_model,
        use_ocr=existing_validation.use_ocr,
        file_name=existing_validation.file_name,
        file_reference=existing_validation.file_reference,
        page=existing_validation.page,
        override=None,
    )


async def delete_existing_entry(data_point_id: str) -> None:
    """Delete existing validated data point entry from the database."""
    logger.info("Deleting existing validated entry for data point ID: %s", data_point_id)
    await asyncio.to_thread(
        database_engine.delete_entity,
        entity_id=data_point_id,
        entity_class=database_tables.ValidatedDataPoint,
    )
