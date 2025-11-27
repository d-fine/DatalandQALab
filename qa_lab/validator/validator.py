import logging
import sys
import time

from qa_lab.database.database_engine import add_entity, get_entity
from qa_lab.database.database_tables import CachedDocument
from qa_lab.dataland.api import QaStatus, get_data_point, get_document, update_data_point_qa_report
from qa_lab.utils.prompts import get_prompts
from qa_lab.validator.ai import execute_prompt
from qa_lab.validator.ocr import extract_pdf

logger = logging.getLogger(__name__)
prompts = get_prompts()


def validate_datapoint(data_point_id: str, ai_model: str, use_ocr: bool = True) -> dict:
    """Validate a datapoint using predefined prompts."""
    # todo: use the openapi thing instead
    data_point = get_data_point(data_point_id)

    # try getting the variables
    data_point_type = data_point.get("dataPointType", "")
    page = int(data_point.get("dataPoint", {}).get("dataSource", {}).get("page", 0))
    file_reference = data_point.get("dataPoint", {}).get("dataSource", {}).get("fileReference", "")
    file_name = data_point.get("dataPoint", {}).get("dataSource", {}).get("fileName", "")

    prompt = prompts.get(data_point_type, {}).get("prompt", None)
    if prompt is None:
        logger.error("No prompt found for data point type: %s", data_point_type)
        sys.exit(1)

    markdown = get_file_using_ocr(file_name=file_name, file_reference=file_reference, page=page)

    res = execute_prompt(prompt.format(context=markdown), ai_model=ai_model)

    qa_status = QaStatus.Pending
    if data_point.get("dataPoint", {}).get("value", "") == res.get("answer", ""):
        qa_status = QaStatus.Accepted
    else:
        qa_status = QaStatus.Rejected

    update_data_point_qa_report(
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
    cached_document = get_entity(CachedDocument, file_reference=file_reference, page=page)

    if cached_document:
        return cached_document.ocr_output
    document = get_document(file_reference, [page])

    markdown = extract_pdf(document)
    add_entity(
        CachedDocument(
            file_name=file_name,
            file_reference=file_reference,
            ocr_output=markdown,
            page=page,
        )
    )
    return markdown
