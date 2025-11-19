import logging

from dataland_backend.models.company_associated_data_nuclear_and_gas_data import CompanyAssociatedDataNuclearAndGasData

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)


def get_nuclear_and_gas_dataset_by_id(data_id: str) -> CompanyAssociatedDataNuclearAndGasData | None:
    """Return the nuclear and gas dataset based on the data id."""
    client = config.get_config().dataland_client

    dataset = None

    try:
        dataset = client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(data_id=data_id)
        logger.info("Dataset retrieved for the given data id %s", data_id)
    except Exception as e:
        logger.exception(
            msg="Error retrieving dataset for the given data id %s", exc_info=e, extra={"data_id": data_id}
        )
    return dataset
