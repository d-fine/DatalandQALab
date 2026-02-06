import asyncio
import logging
import time

from dataland_qa_lab.data_point_flow import models, prompts
from dataland_qa_lab.database import database_engine, database_tables
from dataland_qa_lab.utils import config

conf = config.get_config()


logger = logging.getLogger(__name__)
validation_prompts = prompts.get_prompts()


async def store_data_point_in_db(data: models.ValidatedDatapoint | models.CannotValidateDatapoint) -> None:
    """Store the validated data point in the database."""
    logger.info("Storing validated data point ID: %s in the database.", data.data_point_id)
    if isinstance(data, models.CannotValidateDatapoint):
        model = database_tables.ValidatedDataPoint(
            data_point_id=data.data_point_id,
            data_point_type=data.data_point_type,
            previous_answer=None,
            predicted_answer=None,
            confidence=0.0,
            reasoning=data.reasoning,
            qa_status="QaNotAttempted",
            timestamp=int(time.time()),
            ai_model=data.ai_model,
            use_ocr=data.use_ocr,
            override=data.override,
            file_reference=None,
            file_name=None,
            page=None,
        )
    else:
        model = database_tables.ValidatedDataPoint(
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
            override=data.override,
            file_reference=data.file_reference,
            file_name=data.file_name,
            page=data.page,
        )
    if database_engine.get_entity(database_tables.ValidatedDataPoint, data_point_id=data.data_point_id):
        await delete_existing_entry(data.data_point_id)
    await asyncio.to_thread(database_engine.add_entity, entity=model)


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
            override=existing_validation.override,
            qa_status=existing_validation.qa_status,
            timestamp=existing_validation.timestamp,
            _prompt=existing_validation._prompt,
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
        override=existing_validation.override,
        file_name=existing_validation.file_name,
        file_reference=existing_validation.file_reference,
        page=existing_validation.page,
        qa_report_id=existing_validation.qa_report_id,
        _prompt=existing_validation._prompt,
    )


async def delete_existing_entry(data_point_id: str) -> None:
    """Delete existing validated data point entry from the database."""
    logger.info("Deleting existing validated entry for data point ID: %s", data_point_id)
    await asyncio.to_thread(
        database_engine.delete_entity,
        entity_id=data_point_id,
        entity_class=database_tables.ValidatedDataPoint,
    )
