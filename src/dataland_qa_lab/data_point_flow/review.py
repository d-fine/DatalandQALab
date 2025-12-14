import asyncio
import logging
import time

from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import ai, dataland, db, models, ocr, prompts
from dataland_qa_lab.utils import config, image_helper, pdf_handler

config = config.get_config()


logger = logging.getLogger(__name__)
validation_prompts = prompts.get_prompts()


def _raise_value_error(message: str) -> None:
    """Helper function to raise ValueError with a given message."""
    raise ValueError(message)


def _raise_runtime_error(message: str) -> None:
    """Helper function to raise RuntimeError with a given message."""
    raise RuntimeError(message)


async def validate_datapoint(
    data_point_id: str, use_ocr: bool, ai_model: str, override: bool
) -> models.ValidatedDatapoint | models.CannotValidateDatapoint:
    """Validates a datapoint given a data_point_id."""
    logger.info("Validating datapoint with ID: %s", data_point_id)

    already_checked_data_point = await db.check_if_already_validated(data_point_id)
    if already_checked_data_point:
        if override:
            await db.delete_existing_entry(data_point_id)
        else:
            return already_checked_data_point

    try:
        data_point = await dataland.get_data_point(data_point_id)
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
        await db.store_data_point_in_db(res)
        return res

    prompt = prompts.get_prompt_config(data_point.data_point_type)

    if prompt:
        downloaded_document = await dataland.get_document(
            reference_id=data_point.file_reference, page_num=data_point.page
        )
        try:
            if use_ocr:
                logger.info("Processing via OCR path.")
                ocr_text = await ocr.run_ocr_on_document(
                    file_name=data_point.file_name,
                    file_reference=data_point.file_reference,
                    page=data_point.page,
                    document=downloaded_document,
                )
                prompt_text = prompt.prompt.format(context=ocr_text)
                ai_response = await ai.execute_prompt(prompt=prompt_text, ai_model=ai_model)
            else:
                if not config.vision.enabled:
                    msg = "Image input requested but vision features are disabled in config."
                    _raise_runtime_error(msg)
                logger.info("Processing via Vision AI path.")

                pil_images = await asyncio.to_thread(
                    pdf_handler.render_pdf_to_image, downloaded_document, dpi=config.vision.dpi
                )

                if not pil_images:
                    msg = "No images were rendered from the PDF document."
                    _raise_value_error(msg)

                encoded_images = [image_helper.encode_image_to_base64(img) for img in pil_images]
                prompt_text = prompt.prompt.format(context="Please analyze the attached image of the report page.")
                ai_response = await ai.execute_prompt(prompt=prompt_text, ai_model=ai_model, images=encoded_images)

        except Exception as e:
            logger.exception("Validation processing failed")
            res = models.CannotValidateDatapoint(
                data_point_id=data_point.data_point_id,
                data_point_type=data_point.data_point_type,
                reasoning=f"Processing failed: ({'OCR' if use_ocr else 'Vision'}): {e}",
                ai_model=ai_model,
                use_ocr=use_ocr,
                timestamp=int(time.time()),
                override=override,
            )
            await db.store_data_point_in_db(res)
            return res

        qa_status = QaStatus.ACCEPTED if ai_response.predicted_answer == data_point.value else QaStatus.REJECTED

        await dataland.override_dataland_qa(
            data_point_id=data_point.data_point_id, reasoning=ai_response.reasoning, qa_status=qa_status
        )

        res = models.ValidatedDatapoint(
            data_point_id=data_point.data_point_id,
            data_point_type=data_point.data_point_type,
            previous_answer=data_point.value,
            predicted_answer=ai_response.predicted_answer,
            confidence=ai_response.confidence,
            reasoning=ai_response.reasoning,
            qa_status=qa_status,
            timestamp=int(time.time()),
            ai_model=ai_model,
            use_ocr=use_ocr,
            file_name=data_point.file_name,
            file_reference=data_point.file_reference,
            page=data_point.page,
            override=override,
        )
        await db.store_data_point_in_db(res)
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
    await db.store_data_point_in_db(res)
    return res
