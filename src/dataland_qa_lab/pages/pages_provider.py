import io

import pypdf

from clients.backend.dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_qa_lab.dataland import dataland_client


class PagesProvider:
    """Provide Pages."""

    def __init__(self) -> None:
        """Initiate class."""

    def get_relevant_pages_of_pdf(self, dataset: NuclearAndGasData) -> pypdf.PdfReader:
        """Get page numbers of relevant data."""
        page_numbers = []
        page_numbers.extend(self.__get_relevant_pages_of_yes_no(dataset=dataset),
                            self.__get_relevant_pages_of_numeric(dataset=dataset))

        file_reference = dataset.general.general.nuclear_energy_related_activities_section426.data_source.file_reference

        pdf = dataland_client.documents_api.get_document(file_reference)
        pdf_stream = io.BytesIO(pdf)

        return pdf_stream

    @classmethod
    def __get_relevant_pages_of_yes_no(self, dataset: NuclearAndGasData) -> list[int]:
        """Get page numbers of yes and no questions."""
        data = dataset.general.general
        page_numbers = []

        page_numbers.extend(
            (
                data.nuclear_energy_related_activities_section426.data_source,
                data.nuclear_energy_related_activities_section427.data_source,
                data.nuclear_energy_related_activities_section428.data_source,
                data.fossil_gas_related_activities_section429.data_source,
                data.fossil_gas_related_activities_section430.data_source,
                data.fossil_gas_related_activities_section431.data_source,
            )
        )

        return page_numbers

    @classmethod
    def __get_relevant_pages_of_numeric(self, dataset: NuclearAndGasData) -> list[int]:
        """Get page numbers of numeric values."""
        return [1]
