import io
import json
import logging
import time

import pypdf
from attr import dataclass
from dataland_qa.models.qa_status import QaStatus

from qa_lab.database import database_engine, database_tables
from qa_lab.dataland import dataland_client
from qa_lab.utils import config, prompts
from qa_lab.validator import ai, ocr

logger = logging.getLogger(__name__)
validation_prompts = prompts.get_prompts()

config = config.get_config()
dataland_client = dataland_client.DatalandClient(config.dataland_url, config.dataland_api_key)


@dataclass
class ValidatedDatapoint:
    """Structure to hold validated datapoint information."""

    data_point_id: str
    previous_answer: str
    predicted_answer: str
    confidence: float
    reasoning: str
    qa_status: str
    timestamp: int
    ai_model: str
    use_ocr: bool


def validate_datapoint(
    data_point_id: str, ai_model: str, use_ocr: bool = True, override: bool = False
) -> ValidatedDatapoint:
    """Validate a datapoint using predefined prompts."""
    data_point = dataland_client.data_points_api.get_data_point(data_point_id)
    dp_json = json.loads(data_point.data_point)

    data_point_type = data_point.data_point_type
    page = int(dp_json["dataSource"].get("page", 0))
    file_reference = dp_json["dataSource"].get("fileReference", "")
    file_name = dp_json["dataSource"].get("fileName", "")
    previous_answer = dp_json.get("value", "")

    prompt_template = validation_prompts.get(data_point_type, {}).get("prompt")
    if prompt_template is None:
        msg = f"No prompt found for data point type: {data_point_type}"
        raise ValueError(msg)

    context = _get_file_using_ocr(file_name=file_name, file_reference=file_reference, page=page)

    prompt = prompt_template.format(context=context)
    ai_response = ai.execute_prompt(prompt, ai_model=ai_model)

    predicted_answer = ai_response.get("answer", "")

    qa_status = QaStatus.ACCEPTED if predicted_answer == previous_answer else QaStatus.REJECTED

    if override:
        dataland_client.qa_api.change_data_point_qa_status(
            data_point_id, qa_status=qa_status, comment=ai_response.get("reasoning", "")
        )

    return ValidatedDatapoint(
        data_point_id=data_point_id,
        previous_answer=previous_answer,
        predicted_answer=predicted_answer,
        confidence=ai_response.get("confidence", 0.0),
        reasoning=ai_response.get("reasoning", ""),
        qa_status=qa_status,
        timestamp=int(time.time()),
        ai_model=ai_model,
        use_ocr=use_ocr,
    )


def _get_file_using_ocr(file_name: str, file_reference: str, page: int) -> str:
    """Retrieve file using OCR and check db for cache."""
    cached_document = database_engine.get_entity(
        database_tables.CachedDocument, file_reference=file_reference, page=page
    )

    if cached_document:
        return cached_document.ocr_output

    document = _get_document(reference_id=file_reference, page_numbers=[page])
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


def _get_document(reference_id: str, page_numbers: list[int]) -> io.BytesIO:
    """Return a PDF document stream for specific pages."""
    full_pdf = dataland_client.documents_api.get_document(reference_id)
    full_pdf_stream = io.BytesIO(full_pdf)

    original_pdf = pypdf.PdfReader(full_pdf_stream)
    output_pdf = pypdf.PdfWriter()

    for page_num in page_numbers:
        if 0 <= page_num - 1 < len(original_pdf.pages):
            output_pdf.add_page(original_pdf.pages[page_num - 1])

    extracted_pdf_stream = io.BytesIO()
    output_pdf.write(extracted_pdf_stream)
    extracted_pdf_stream.seek(0)

    return extracted_pdf_stream
