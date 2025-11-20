import logging

from dataland_backend.models.sfdr_data import SfdrData

logger = logging.getLogger(__name__)


class SFDRDataCollection:
    """Class to bundle data regarding a dataset of SFDR."""

    def __init__(self, data: SfdrData) -> None:
        """Initialize the SFDR data collection."""
        self.data = data

    def get_value_generic(self, category: str, subcategory: str, field_name: str) -> float | None:
        """Generic method to safely get a numeric value."""
        try:
            cat_obj = getattr(self.data, category, None)
            if not cat_obj:
                return None
            subcat_obj = getattr(cat_obj, subcategory, None)
            if not subcat_obj:
                return None
            datapoint = getattr(subcat_obj, field_name, None)
            return datapoint.value if datapoint else None
        except Exception as e:
            logger.warning("Error accessing value %s.%s.%s: %s", category, subcategory, field_name, e)
            return None

    def get_scope1_ghg_emissions(self) -> float | None:
        return self.get_value_generic("environmental", "greenhouse_gas_emissions", "scope1_ghg_emissions_in_tonnes")

    def get_scope1_page_number(self) -> int | str | None:
        """Return the page number for Scope 1 GHG emissions."""
        try:
            if (
                self.data.environmental
                and self.data.environmental.greenhouse_gas_emissions
                and self.data.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes
                and self.data.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes.data_source
            ):
                return self.data.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes.data_source.page
            return None
        except AttributeError:
            return None

    def get_scope1_file_reference(self) -> str | None:
        """Return the file reference for Scope 1 GHG emissions."""
        try:
            if (
                self.data.environmental
                and self.data.environmental.greenhouse_gas_emissions
                and self.data.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes
                and self.data.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes.data_source
            ):
                return self.data.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes.data_source.file_reference
            return None
        except AttributeError:
            return None
