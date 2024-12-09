import io

import pypdf
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData

from dataland_qa_lab.dataland.data_provider import DataProvider
from dataland_qa_lab.utils import config


class PagesProvider:
    """Provide the page numbers of relevant content in the company report."""

    def get_relevant_pages_of_pdf(self, dataset: NuclearAndGasData) -> pypdf.PdfReader:
        """Get page numbers of relevant data."""
        yes_no_pages = self.get_relevant_pages_of_nuclear_and_gas_yes_no_questions(dataset=dataset)
        numeric_pages = self.get_relevant_pages_of_numeric(dataset=dataset)
        page_numbers = sorted(set(yes_no_pages + numeric_pages))

        file_reference = dataset.general.general.nuclear_energy_related_activities_section426.data_source.file_reference

        dataland_client = config.get_config().dataland_client
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

    @classmethod
    def get_relevant_pages_of_nuclear_and_gas_yes_no_questions(cls, dataset: NuclearAndGasData) -> list[int]:
        """Get page numbers of yes and no questions."""
        data_sources = DataProvider().get_datasources_of_dataset(dataset)
        return cls.__collect_page_numbers(data_sources)

    @classmethod
    def get_relevant_pages_of_numeric(cls, dataset: NuclearAndGasData) -> list[int]:
        """Get page numbers of numeric values."""
        data_sources = DataProvider().get_datasources_of_nuclear_and_gas_numeric_values(dataset)
        return cls.__collect_page_numbers(data_sources)

    @classmethod
    def __collect_page_numbers(cls, data_sources: any) -> list[int]:
        unique_pages = set()
        page_numbers = []

        for data_source in data_sources:
            if data_source is not None and data_source.page is not None:
                page = int(data_source.page)
                if page not in unique_pages:
                    unique_pages.add(page)
                    page_numbers.append(page)

        return page_numbers
