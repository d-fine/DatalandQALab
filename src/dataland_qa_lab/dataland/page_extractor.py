from dataland_backend.models.company_associated_data_nuclear_and_gas_data import CompanyAssociatedDataNuclearAndGasData
from pydantic import StrictStr


class PageExtractor:
    """Get page numbers."""

    def __init__(self, dataset: CompanyAssociatedDataNuclearAndGasData) -> None:
        self.dataset = dataset

    def get_relevant_pages_for_yn_values(self) -> list[StrictStr]:
        """Get pages"""
        pages = []

        pages.extend((
             self.dataset.data.general.general.nuclear_energy_related_activities_section426.page,
             self.dataset.data.general.general.nuclear_energy_related_activities_section427.page,
             self.dataset.data.general.general.nuclear_energy_related_activities_section428.page,
             self.dataset.data.general.general.fossil_gas_related_activities_section429.page,
             self.dataset.data.general.general.fossil_gas_related_activities_section430.page,
             self.dataset.data.general.general.fossil_gas_related_activities_section431.page))
        
        return pages
    
    def get_
