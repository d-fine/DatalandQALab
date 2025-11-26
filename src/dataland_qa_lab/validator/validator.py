import logging
import sys
import time

from dataland_qa_lab.dataland.api import QaStatus, get_data_point, get_document, update_data_point_qa_report
from dataland_qa_lab.utils.prompts import get_prompts
from dataland_qa_lab.validator.ai import execute_prompt
from dataland_qa_lab.validator.ocr import extract_pdf

logger = logging.getLogger(__name__)
prompts = get_prompts()


def validate_datapoint(data_point_id: str, ai_model: str, use_ocr: bool = True) -> dict:
    """Validate a datapoint using predefined prompts."""
    # todo: use the openai thing instead
    data_point = get_data_point(data_point_id)

    # try getting the variables
    data_point_type = data_point.get("dataPointType", "")
    page = data_point.get("dataPoint", {}).get("dataSource", {}).get("page", 0)
    page_reference = data_point.get("dataPoint", {}).get("dataSource", {}).get("fileReference", "")

    prompt = prompts.get(data_point_type, {}).get("prompt", None)
    if prompt is None:
        logger.error("No prompt found for data point type: %s", data_point_type)
        sys.exit(1)

    document = get_document(page_reference, [int(page)])

    markdown = extract_pdf(document)

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
