import logging

from dataland_backend.models.company_associated_data_nuclear_and_gas_data import CompanyAssociatedDataNuclearAndGasData

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)


def get_dataset_by_id(data_id: str) -> CompanyAssociatedDataNuclearAndGasData:
    """Return the nuclear and gas dataset based on the data id."""
    client = config.get_config().dataland_client

    try:
        dataset = client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(data_id=data_id)
        msg = f"Dataset retrieved for the given data id {data_id}"
        logger.info(msg)
    except Exception as e:
        msg = f"Error retrieving dataset for the given data id {data_id} from dataland"
        logger.exception(msg=msg, exc_info=e)

    return dataset
