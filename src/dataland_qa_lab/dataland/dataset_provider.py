from pydantic import StrictStr

from clients.backend.dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_qa_lab.dataland import dataland_client


class DatasetProvider:
    """Class to bundle methods that provide information about a certain dataset."""

    def __init__(self, data_id: StrictStr) -> None:
        """Initialize the class with the data id."""
        self.data_id = data_id

    def get_dataset_by_id(self) -> NuclearAndGasData:
        """Return the nuclear and gas dataset based on the data id."""
        dataset = dataland_client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(
            data_id=self.data_id
        )

        return dataset
