import io
import logging

import pypdf
from dataland_backend.models.extended_document_reference import ExtendedDocumentReference

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection

logger = logging.getLogger(__name__)


def get_relevant_page_numbers(dataset: NuclearAndGasDataCollection) -> list[int]:
    """Get page numbers of relevant data."""
    logger.info("Starting to extract page numbers.")
    yes_no_pages = get_relevant_pages_of_nuclear_and_gas_yes_no_questions(dataset=dataset)
    numeric_pages = get_relevant_pages_of_numeric(dataset=dataset)
    logger.info("Relevant page numbers extracted.")

    return sorted(set(yes_no_pages + numeric_pages))


def get_relevant_pages_of_pdf(dataset: NuclearAndGasDataCollection) -> pypdf.PdfReader | None:
    """Get page numbers of relevant data."""
    dataland_client = config.get_config().dataland_client
    logger.info("Starting to retrieve pages from company report.")

    page_numbers = get_relevant_page_numbers(dataset=dataset)
    try:
        datapoint = dataset.yes_no_data_points.get("nuclear_energy_related_activities_section426").datapoint
        file_reference = datapoint.data_source.file_reference
    except AttributeError:
        logger.exception("No file reference found.")
        return None

    full_pdf = dataland_client.documents_api.get_document(file_reference)
    full_pdf_stream = io.BytesIO(full_pdf)

    original_pdf = pypdf.PdfReader(full_pdf_stream)
    output_pdf = pypdf.PdfWriter()

    for page_num in page_numbers:
        if 0 <= page_num - 1 < len(original_pdf.pages):
            output_pdf.add_page(original_pdf.pages[page_num - 1])

    extracted_pdf_stream = io.BytesIO()
    output_pdf.write(extracted_pdf_stream)
    extracted_pdf_stream.seek(0)

    if extracted_pdf_stream is not None:
        logger.info("Pages successfully retrieved from the company report.")
    else:
        logger.error("Error retrieving pages from company report.")

    return extracted_pdf_stream


def get_relevant_pages_of_nuclear_and_gas_yes_no_questions(dataset: NuclearAndGasDataCollection) -> list[int]:
    """Get page numbers of yes and no questions."""
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_yes_no_questions(dataset)
    return collect_page_numbers(data_sources)


def get_relevant_pages_of_numeric(dataset: NuclearAndGasDataCollection) -> list[int]:
    """Get page numbers of numeric values."""
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_numeric_values(dataset)
    return collect_page_numbers(data_sources)


def collect_page_numbers(data_points: dict[str, ExtendedDocumentReference | None]) -> list[int]:
    """Helper function to gather page numbers."""
    unique_pages = set()
    for data in data_points.values():
        if data and data.page is not None:
            if "-" in data.page:
                start, end = map(int, data.page.split("-"))
                unique_pages.update(range(start, end + 1))
            else:
                unique_pages.add(int(data.page))
    return sorted(unique_pages)
