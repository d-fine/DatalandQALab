import io

import pypdf
from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.utils import config


def get_relevant_pages_of_pdf(dataset: NuclearAndGasData) -> pypdf.PdfReader:
    """Get page numbers of relevant data."""
    dataland_client = config.get_config().dataland_client

    yes_no_pages = get_relevant_pages_of_nuclear_and_gas_yes_no_questions(dataset=dataset)
    numeric_pages = get_relevant_pages_of_numeric(dataset=dataset)

    page_numbers = sorted(set(yes_no_pages + numeric_pages))
    file_reference = dataset.general.general.nuclear_energy_related_activities_section426.data_source.file_reference

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

    return extracted_pdf_stream


def get_relevant_pages_of_nuclear_and_gas_yes_no_questions(dataset: NuclearAndGasData) -> list[int]:
    """Get page numbers of yes and no questions."""
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_yes_no_questions(dataset)
    return collect_page_numbers(data_sources)


def get_relevant_pages_of_numeric(dataset: NuclearAndGasData) -> list[int]:
    """Get page numbers of numeric values."""
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_numeric_values(dataset)
    return collect_page_numbers(data_sources)


def collect_page_numbers(data_sources: dict[str, ExtendedDocumentReference | None]) -> list[int]:
    """Helper function to gather page numbers."""
    unique_pages = set()
    for data_source in data_sources.values():
        if data_source and data_source.page is not None:
            unique_pages.add(int(data_source.page))

    return sorted(unique_pages)
