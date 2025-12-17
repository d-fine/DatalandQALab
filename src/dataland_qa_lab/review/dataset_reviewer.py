import io
import json
import logging
import time
from dataclasses import dataclass

import pypdf
from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import ai, prompts
from dataland_qa_lab.database import database_engine, database_tables
from dataland_qa_lab.dataland import dataset_provider
from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.review.exceptions import (
    DataCollectionError,
    DatasetNotFoundError,
    OCRProcessingError,
    ReportSubmissionError,
)
from dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator import NuclearAndGasReportGenerator
from dataland_qa_lab.utils import config, slack
from dataland_qa_lab.utils.datetime_helper import get_german_time_as_string
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection

config = config.get_config()
validation_prompts = prompts.get_prompts()


logger = logging.getLogger(__name__)


def old_review_dataset_via_api(
    data_id: str, force_review: bool = False, ai_model: str | None = None, use_ocr: bool = True
) -> dict:
    """Review a dataset via API call."""
    report_id = old_review_dataset(data_id=data_id, force_review=force_review, ai_model=ai_model, use_ocr=use_ocr)

    if report_id is None:
        return {"error": "Failed to retrieve data"}
    return json.loads(
        config.dataland_client.eu_taxonomy_nuclear_gas_qa_api.get_nuclear_and_gas_data_qa_report(
            data_id=data_id, qa_report_id=report_id
        ).to_json()
    )


def old_review_dataset(  # noqa: PLR0915
    data_id: str,
    force_review: bool = False,
    ai_model: str | None = None,
    use_ocr: bool = True,
) -> str:
    """Review a dataset."""
    logger.info("Starting the review of the Dataset: %s", data_id)

    dataset = dataset_provider.get_dataset_by_id(data_id)
    if dataset is None:
        msg = f"Dataset with data_id '{data_id}' was not found."
        logger.warning(msg)
        raise DatasetNotFoundError(msg)

    existing_report = database_engine.get_entity(database_tables.ReviewedDataset, data_id=data_id)

    if force_review and existing_report is not None:
        logger.info("Deleting old review from the database")
        database_engine.delete_entity(data_id, database_tables.ReviewedDataset)
        existing_report = None

    if existing_report is None:
        logger.info("Dataset with the Data-ID does not exist in the database. Starting review.")
        datetime_now = get_german_time_as_string()

        message = f"🔍 Starting review of the Dataset with the Data-ID: {data_id}"
        slack.send_slack_message(message=message)

        review_dataset = database_tables.ReviewedDataset(data_id=data_id, review_start_time=datetime_now)

        logger.info("Adding the dataset to the database.")
        database_engine.add_entity(review_dataset)

        try:
            data_collection = NuclearAndGasDataCollection(dataset.data)
        except Exception as exc:
            msg = f"Could not build NuclearAndGasDataCollection for data_id '{data_id}': {exc}"
            logger.exception(msg)
            raise DataCollectionError(msg) from exc

        logger.info("Data collection created.")

        page_numbers = pages_provider.get_relevant_page_numbers(data_collection)
        relevant_pages_pdf_reader = pages_provider.get_relevant_pages_of_pdf(data_collection)
        generator = NuclearAndGasReportGenerator(ai_model=ai_model)

        if relevant_pages_pdf_reader is None or not use_ocr:
            report = generator.generate_report(relevant_pages=None, dataset=data_collection)
        else:
            try:
                readable_text = text_to_doc_intelligence.old_get_markdown_from_dataset(
                    data_id=data_id,
                    page_numbers=page_numbers,
                    relevant_pages_pdf_reader=relevant_pages_pdf_reader,
                )
            except Exception as exc:
                msg = f"OCR/Text extraction failed for data_id '{data_id}': {exc}"
                logger.exception(msg)
                raise OCRProcessingError(msg) from exc

            report = generator.generate_report(
                relevant_pages=readable_text,
                dataset=data_collection,
            )
        try:
            data = config.dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report(
                data_id=data_id,
                nuclear_and_gas_data=report,
            )
        except Exception as exc:
            msg = f"Failed to post QA report for data_id '{data_id}': {exc}"
            logger.exception(msg)
            raise ReportSubmissionError(msg) from exc

        old_update_reviewed_dataset_in_database(data_id=data_id, report_id=data.qa_report_id)

        message = f"✅ Review is successful for the dataset with the Data-ID: {data_id}. Report ID: {data.qa_report_id}"
        slack.send_slack_message(message=message)

        logger.info("Report posted successfully for dataset with ID: %s", data_id)
        logger.info("Report ID: %s", data.qa_report_id)
        return data.qa_report_id

    logger.info("Report for data_id already exists.")
    return existing_report.report_id


def old_update_reviewed_dataset_in_database(data_id: str, report_id: str) -> None:
    """After review set the database entry to finished and add review end time."""
    datetime_now = get_german_time_as_string()

    review_dataset = database_tables.ReviewedDataset(
        data_id=data_id, review_end_time=datetime_now, report_id=report_id, review_completed=True
    )

    database_engine.update_entity(review_dataset)


# below starts the new validation flow to validate individual datapoints


@dataclass
class ValidatedDatapoint:
    """Structure to hold validated datapoint information."""

    data_point_id: str
    data_point_type: str
    previous_answer: str
    predicted_answer: str
    confidence: float
    reasoning: str
    qa_status: str
    timestamp: int
    ai_model: str
    use_ocr: bool
    file_name: str
    file_reference: str
    page: int


def validate_datapoint(
    data_point_id: str, ai_model: str, use_ocr: bool = True, override: bool = False
) -> ValidatedDatapoint:
    """Validate a datapoint using predefined prompts."""
    data_point = config.dataland_client.data_points_api.get_data_point(data_point_id)
    dp_json = json.loads(data_point.data_point)

    data_point_type = data_point.data_point_type
    if dp_json.get("dataSource") is None:
        msg = f"Data point {data_point_id} is missing dataSource information."
        raise ValueError(msg)
    # page can be None in some data; ensure we convert safely to int
    page = int(dp_json["dataSource"].get("page") or 0)
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
        config.dataland_client.qa_api.change_data_point_qa_status(
            data_point_id, qa_status=qa_status, comment=ai_response.get("reasoning", "")
        )

    return ValidatedDatapoint(
        data_point_id=data_point_id,
        data_point_type=data_point_type,
        previous_answer=previous_answer,
        predicted_answer=predicted_answer,
        confidence=ai_response.get("confidence", 0.0),
        reasoning=ai_response.get("reasoning", ""),
        qa_status=qa_status,
        timestamp=int(time.time()),
        ai_model=ai_model,
        use_ocr=use_ocr,
        file_reference=file_reference,
        file_name=file_name,
        page=page,
    )


def _get_file_using_ocr(file_name: str, file_reference: str, page: int) -> str:
    """Retrieve file using OCR and check db for cache."""
    cached_document = database_engine.get_entity(
        database_tables.CachedDocument, file_reference=file_reference, page=page
    )

    if cached_document:
        return cached_document.ocr_output

    document = _get_document(reference_id=file_reference, page_numbers=[page])
    markdown = text_to_doc_intelligence.extract_pdf(document)

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
    full_pdf = config.dataland_client.documents_api.get_document(reference_id)
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
