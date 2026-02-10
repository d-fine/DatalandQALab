import asyncio
import json
import logging
import time
from dataclasses import asdict
from io import BytesIO
from types import SimpleNamespace

from dataland_qa_lab.data_point_flow import ai, dataland, db, models, ocr, pdf_handler, prompts
from dataland_qa_lab.utils import image_helper

logger = logging.getLogger(__name__)
validation_prompts = prompts.get_prompts()


def build_prompt_text(prompt_template: str, context: str, depends_on: str, data_point: models.DataPoint) -> str:
    """Returns the formatted prompt text."""
    return prompt_template.format(
        context=context,
        depends_on=depends_on,
        data_point_id=data_point.data_point_id,
        data_point_type=data_point.data_point_type,
        data_source=json.dumps(data_point.data_source) if isinstance(data_point.data_source, dict) else {},
        page=data_point.page,
        file_reference=data_point.file_reference,
        file_name=data_point.file_name,
        value=data_point.value,
        comment=data_point.comment,
        quality=data_point.quality,
    )


async def run_ocr_validation(
    data_point: models.DataPoint, document: BytesIO, prompt: models.DataPointPrompt, depends_on: str, ai_model: str
) -> tuple[models.AIResponse, str]:
    """Run OCR validation on the given data point."""
    ocr_text = await ocr.run_ocr_on_document(
        file_name=data_point.file_name,
        file_reference=data_point.file_reference,
        page=data_point.page,
        document=document,
    )

    prompt_text = build_prompt_text(
        prompt.prompt,
        context=ocr_text,
        depends_on=depends_on,
        data_point=data_point,
    )

    return await ai.execute_prompt(
        prompt=prompt_text,
        previous_answer=data_point.value,
        ai_model=ai_model,
    ), prompt_text


async def run_vision_validation(
    data_point: models.DataPoint, document: BytesIO, prompt: models.DataPointPrompt, depends_on: str, ai_model: str
) -> tuple[models.AIResponse, str]:
    """Run Vision AI validation on the given data point."""
    images = await asyncio.to_thread(pdf_handler.render_pdf_to_image, document)
    if not images:
        msg = "No images rendered from PDF"
        raise RuntimeError(msg)

    encoded_images = [image_helper.encode_image_to_base64(img) for img in images]

    prompt_text = build_prompt_text(
        prompt.prompt,
        context="{Please analyze the attached image of the report page}.",
        depends_on=depends_on,
        data_point=data_point,
    )

    return await ai.execute_prompt(
        prompt=prompt_text,
        previous_answer=data_point.value,
        ai_model=ai_model,
        images=encoded_images,
    ), prompt_text


async def store_failure(  # noqa: PLR0913, PLR0917
    data_point: models.DataPoint,
    reason: str,
    ai_model: str,
    use_ocr: bool,
    override: bool,
    prompt_text: str | None = None,
) -> models.CannotValidateDatapoint:
    """Store a failure reason for the given data point."""
    res = models.CannotValidateDatapoint(
        data_point_id=data_point.data_point_id,
        data_point_type=data_point.data_point_type,
        reasoning=reason,
        ai_model=ai_model,
        use_ocr=use_ocr,
        override=override,
        qa_status="QaNotAttempted",
        _prompt=prompt_text,
        timestamp=int(time.time()),
    )
    await db.store_data_point_in_db(res)
    return res


async def fetch_dependency_datapoints(dataset_id: str, depends_on: list, use_ocr: bool, ai_model: str) -> str:
    """Fetch dependency datapoint - to be implemented."""
    additional_context = ""
    data_points = await dataland.get_contained_data_points(dataset_id)

    for i in depends_on:
        datapoint_id = data_points.get(i)
        if datapoint_id:
            additional_context += f"This is the validated output for the data point of type {i}:\n"
            additional_context += json.dumps(
                asdict(
                    await validate_datapoint(
                        data_point_id=datapoint_id,
                        use_ocr=use_ocr,
                        ai_model=ai_model,
                        override=False,
                        dataset_id=dataset_id,
                    )
                )
            )
            additional_context += "\n"

    return additional_context


async def validate_datapoint(
    data_point_id: str, use_ocr: bool, ai_model: str, override: bool, dataset_id: str | None = None
) -> models.CannotValidateDatapoint | models.ValidatedDatapoint:
    """Validate a single data point."""
    logger.info("Validating datapoint %s", data_point_id)

    existing = await db.check_if_already_validated(data_point_id)
    if existing and not override:
        return existing
    if existing and override:
        await db.delete_existing_entry(data_point_id)

    try:
        data_point = await dataland.get_data_point(data_point_id)
    except Exception as e:  # noqa: BLE001
        return await store_failure(
            data_point=SimpleNamespace(data_point_id=data_point_id, data_point_type=None),
            reason=f"Couldn't fetch data point: {e}",
            ai_model=ai_model,
            use_ocr=use_ocr,
            override=override,
        )

    prompt = prompts.get_prompt_config(data_point.data_point_type)
    if not prompt:
        return await store_failure(
            data_point=data_point,
            reason="No Prompt configured for this data point type.",
            ai_model=ai_model,
            use_ocr=use_ocr,
            override=override,
        )

    depends_on = ""
    if prompt.depends_on and dataset_id:
        depends_on = await fetch_dependency_datapoints(dataset_id, prompt.depends_on, use_ocr, ai_model)

    document = await dataland.get_document(
        reference_id=data_point.file_reference,
        page_num=data_point.page,
    )

    try:
        if use_ocr:
            ai_response, prompt_text = await run_ocr_validation(data_point, document, prompt, depends_on, ai_model)
        else:
            ai_response, prompt_text = await run_vision_validation(data_point, document, prompt, depends_on, ai_model)
    except Exception as e:
        logger.exception("Validation failed")
        return await store_failure(
            data_point=data_point,
            reason=f"Processing failed ({'OCR' if use_ocr else 'Vision'}): {e}",
            ai_model=ai_model,
            use_ocr=use_ocr,
            override=override,
        )

    qa_report_id = None
    try:
        qa_report = await dataland.override_dataland_qa(
            data_point_id=data_point.data_point_id,
            comment="Reviewed by QaLab: " + ai_response.reasoning,
            qa_status=ai_response.qa_status,
            predicted_answer=ai_response.predicted_answer,
            data_source=data_point.data_source,
        )
        qa_report_id = qa_report.qa_report_id
    except Exception:  # noqa: BLE001
        pass

    res = models.ValidatedDatapoint(
        data_point_id=data_point.data_point_id,
        data_point_type=data_point.data_point_type,
        previous_answer=data_point.value,
        predicted_answer=ai_response.predicted_answer,
        confidence=ai_response.confidence,
        reasoning=ai_response.reasoning,
        qa_status=ai_response.qa_status,
        ai_model=ai_model,
        use_ocr=use_ocr,
        file_name=data_point.file_name,
        file_reference=data_point.file_reference,
        page=data_point.page,
        override=override,
        qa_report_id=qa_report_id,
        _prompt=prompt_text,
        timestamp=int(time.time()),
    )
    await db.store_data_point_in_db(res)
    return res
