import logging

from dataland_backend.models.sfdr_data import SfdrData

logger = logging.getLogger(__name__)


class SFDRDataCollection:
    """Class to bundle data regarding a dataset of SFDR."""

    def __init__(self, data: SfdrData) -> None:
        """Initialize the SFDR data collection."""
        self.data = data

    def get_scope1_ghg_emissions(self) -> float | None:
        """Return the value for scope1 GHG emissions, or None if not available."""
        try:
            return (
                self.data.environmental.greenhouse_gas_emissions
                .scope1_ghg_emissions_in_tonnes.value)
        except AttributeError as e:
            logger.warning("Error accessing scope1 GHG emissions: %s", e)
            return None

    def get_scope1_file_reference(self) -> str | None:
        """Return the file reference for Scope1 GHG emissions."""
        try:
            return (
                self.data.environmental.greenhouse_gas_emissions
                .scope1_ghg_emissions_in_tonnes.data_source.file_reference)
        except AttributeError as e:
            logger.warning("Error accessing scope1 file reference: %s", e)
            return None

    def get_scope1_page_number(self) -> str | int | None:
        """Return the page number for Scope1 GHG emissions."""
        try:
            return (
                self.data.environmental.greenhouse_gas_emissions
                .scope1_ghg_emissions_in_tonnes.data_source.page)
        except AttributeError as e:
            logger.warning("Error accessing scope1 page number: %s", e)
            return None
