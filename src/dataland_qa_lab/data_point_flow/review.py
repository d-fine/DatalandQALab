import logging
import time

from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import ai, dataland, db, models, ocr, prompts
from dataland_qa_lab.utils import config

config = config.get_config()


logger = logging.getLogger(__name__)
validation_prompts = prompts.get_prompts()


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
        if use_ocr:
            ocr_text = await ocr.run_ocr_on_document(
                file_name=data_point.file_name,
                file_reference=data_point.file_reference,
                page=data_point.page,
                document=downloaded_document,
            )

            # Get dependency values if needed
            deps = {}
            if prompt.depends_on:
                deps = await dataland.get_dependency_values(data_point_id, prompt.depends_on)

            # Build the prompt text
            prompt_vars = {"context": ocr_text, "value": data_point.value}
            if "{depends_on}" in prompt.prompt:
                deps_text = "\n".join([f"{k}: {v}" for k, v in deps.items()]) if deps else "not applicable"
                prompt_vars["depends_on"] = deps_text

            prompt_text = prompt.prompt.format(**prompt_vars)
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

        await dataland.override_dataland_qa(
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
