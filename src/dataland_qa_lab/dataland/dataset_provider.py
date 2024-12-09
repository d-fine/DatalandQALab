from dataland_backend.models.company_associated_data_nuclear_and_gas_data import CompanyAssociatedDataNuclearAndGasData
from pydantic import StrictStr

from dataland_qa_lab.utils import config


class DatasetProvider:
    """Class to bundle methods that provide information about a certain dataset."""

    @classmethod
    def get_dataset_by_id(cls, data_id: StrictStr) -> CompanyAssociatedDataNuclearAndGasData:
        """Return the nuclear and gas dataset based on the data id."""
        client = config.get_config().dataland_client
        dataset = client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(
            data_id=data_id
        )

        return dataset
