from dataland_qa.models.nuclear_and_gas_data import NuclearAndGasData
from pydantic import StrictStr

from dataland_qa_lab.utils import config


class DatasetProvider:
    """Class to bundle methods that provide information about a certain dataset."""

    def __init__(self, data_id: StrictStr) -> None:
        """Initialize the class with the data id."""
        self.data_id = data_id
        self.dataland_client = config.get_config().dataland_client

    def get_dataset_by_id(self) -> NuclearAndGasData:
        """Return the nuclear and gas dataset based on the data id."""
        dataset = self.dataland_client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(
            data_id=self.data_id
        )

        return dataset.data
