import logging
import time

from qa_lab.database import database_engine, database_tables
from qa_lab.dataland import api
from qa_lab.utils import prompts
from qa_lab.validator import ai, ocr

logger = logging.getLogger(__name__)
prompts = prompts.get_prompts()


def validate_datapoint(data_point_id: str, ai_model: str, use_ocr: bool = True, override: bool = False) -> dict:
    """Validate a datapoint using predefined prompts."""
    # todo: use the openapi thing instead
    data_point = api.get_data_point(data_point_id)

    data_point_type = data_point.get("dataPointType", "")
    page = int(data_point.get("dataPoint", {}).get("dataSource", {}).get("page", 0))
    file_reference = data_point.get("dataPoint", {}).get("dataSource", {}).get("fileReference", "")
    file_name = data_point.get("dataPoint", {}).get("dataSource", {}).get("fileName", "")

    prompt = prompts.get(data_point_type, {}).get("prompt", None)
    if prompt is None:
        msg = f"No prompt found for data point type: {data_point_type}"
        raise ValueError(msg)

    markdown = get_file_using_ocr(file_name=file_name, file_reference=file_reference, page=page)

    res = ai.execute_prompt(prompt.format(context=markdown), ai_model=ai_model)

    qa_status = api.QaStatus.Pending
    if data_point.get("dataPoint", {}).get("value", "") == res.get("answer", ""):
        qa_status = api.QaStatus.Accepted
    else:
        qa_status = api.QaStatus.Rejected

    if override:
        api.update_data_point_qa_report(
            data_point_id,
            qa_status=qa_status,
            comment=res.get("reasoning", ""),
        )

    return {
        "data_point_id": data_point_id,
        "previous_answer": data_point.get("dataPoint", {}).get("value", ""),
        "predicted_answer": res.get("answer", ""),
        "confidence": res.get("confidence", 0.0),
        "reasoning": res.get("reasoning", ""),
        "qa_status": qa_status,
        "timestamp": int(time.time()),
        "ai_model": ai_model,
        "use_ocr": use_ocr,
    }


def get_file_using_ocr(file_name: str, file_reference: str, page: int) -> str:
    """Retrieve file using OCR and check db for cache."""
    cached_document = database_engine.get_entity(
        database_tables.CachedDocument, file_reference=file_reference, page=page
    )

    if cached_document:
        return cached_document.ocr_output
    document = api.get_document(file_reference, [page])

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
