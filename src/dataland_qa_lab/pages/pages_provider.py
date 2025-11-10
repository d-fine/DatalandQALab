import io
import logging

import pypdf
from dataland_backend.models.extended_document_reference import ExtendedDocumentReference

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection
from dataland_qa_lab.utils.sfdr_data_collection import SFDRDataCollection

logger = logging.getLogger(__name__)


def get_relevant_pages_of_pdf(
    dataset: NuclearAndGasDataCollection | SFDRDataCollection,
) -> pypdf.PdfReader | None:
    """Get page numbers of relevant data."""
    dataland_client = config.get_config().dataland_client
    logger.info("Starting to retrieve pages from company report.")

    # implement router to get correct page numbers based on dataset type
    if isinstance(dataset, NuclearAndGasDataCollection):
        page_numbers = get_nuclear_and_gas_page_numbers(dataset)
        try:
            datapoint = dataset.yes_no_data_points.get("nuclear_energy_related_activities_section426").datapoint
            file_reference = datapoint.data_source.file_reference
        except AttributeError:
            logger.exception("Nuclear & Gas:No file reference found in section 4.26.")
            return None
    elif isinstance(dataset, SFDRDataCollection):
        page_numbers = get_sfdr_page_numbers(dataset)
        file_reference = dataset.get_scope1_file_reference()
        if not file_reference:
            logger.warning("SFDR: No file reference found for Scope1 GHG emissions.")
            return None

    else:
        logger.error(f"Unknown dataset type: {type(dataset)}")
        return None
    # pdf laden und schneiden

    if not page_numbers:
        logger.warning("No relevant pages found to extract.")
        return None

    logger.info("Extracting pages: %s from file reference: %s", page_numbers, file_reference)
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


def get_nuclear_and_gas_page_numbers(dataset: NuclearAndGasDataCollection) -> list[int]:
    """Get page numbers of relevant data in Nuclear & Gas dataset."""
    logger.info("Extracting page numbers for Nuclear & Gas dataset.")
    yes_no_pages = collect_page_numbers(data_provider.get_datasources_of_nuclear_and_gas_yes_no_questions(dataset))
    numeric_pages = collect_page_numbers(data_provider.get_datasources_of_nuclear_and_gas_numeric_values(dataset))
    return sorted(set(yes_no_pages + numeric_pages))


def get_sfdr_page_numbers(dataset: SFDRDataCollection) -> list[int]:
    """Get page numbers of relevant data in SFDR dataset."""
    logger.info("Extracting page numbers for SFDR datasets.")
    pages = set()

    scope1_page = dataset.get_scope1_page_number()
    if scope1_page:
        try:
            pages.add(int(scope1_page))
        except (ValueError, TypeError):
            logger.warning("Could not parse SFDR page number: %s", scope1_page)
    return sorted(pages)


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
