import io

import pypdf
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData

from dataland_qa_lab.utils import config


class PagesProvider:
    """Provide Pages."""

    def __init__(self) -> None:
        """Initiate class."""

    def get_relevant_pages_of_pdf(self, dataset: NuclearAndGasData) -> pypdf.PdfReader:
        """Get page numbers of relevant data."""
        page_numbers = []
        page_numbers.extend((self.get_relevant_pages_of_yes_no(dataset=dataset),
                            self.get_relevant_pages_of_numeric(dataset=dataset)))

        file_reference = dataset.general.general.nuclear_energy_related_activities_section426.data_source.file_reference

        dataland_client = config.get_config().dataland_client
        pdf = dataland_client.documents_api.get_document(file_reference)
        pdf_stream = io.BytesIO(pdf)

        return pdf_stream

    @classmethod
    def get_relevant_pages_of_yes_no(cls, dataset: NuclearAndGasData) -> list[int]:
        """Get page numbers of yes and no questions."""
        data = dataset.general.general

        sections = [
            data.nuclear_energy_related_activities_section426,
            data.nuclear_energy_related_activities_section427,
            data.nuclear_energy_related_activities_section428,
            data.fossil_gas_related_activities_section429,
            data.fossil_gas_related_activities_section430,
            data.fossil_gas_related_activities_section431,
        ]

        page_numbers = [
            int(section.data_source.page)
            for section in sections
            if section is not None and section.data_source is not None
        ]

        return page_numbers

    @classmethod
    def get_relevant_pages_of_numeric(cls, dataset: NuclearAndGasData) -> list[int]:
        """Get page numbers of numeric values."""
        data = dataset.general
        page_numbers = []

        targets = [
            data.taxonomy_aligned_denominator.nuclear_and_gas_taxonomy_aligned_capex_denominator,
            data.taxonomy_aligned_denominator.nuclear_and_gas_taxonomy_aligned_revenue_denominator,
            data.taxonomy_aligned_numerator.nuclear_and_gas_taxonomy_aligned_capex_numerator,
            data.taxonomy_aligned_numerator.nuclear_and_gas_taxonomy_aligned_revenue_numerator,
            data.taxonomy_eligible_but_not_aligned.nuclear_and_gas_taxonomy_eligible_but_not_aligned_capex,
            data.taxonomy_eligible_but_not_aligned.nuclear_and_gas_taxonomy_eligible_but_not_aligned_revenue,
            data.taxonomy_non_eligible.nuclear_and_gas_taxonomy_non_eligible_capex,
            data.taxonomy_non_eligible.nuclear_and_gas_taxonomy_non_eligible_revenue
        ]

        page_numbers.extend(
            int(target.data_source.page)
            for target in targets
            if target is not None and target.data_source is not None
        )

        return page_numbers
