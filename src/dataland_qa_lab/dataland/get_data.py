from dataland_backend.models.company_associated_data_nuclear_and_gas_data import CompanyAssociatedDataNuclearAndGasData

from dataland_qa_lab.utils import config

conf = config.get_config()
dataland_client = conf.dataland_client


def _get_all_company_datasets_(company_id: str) -> str:
    api = dataland_client.eu_taxonomy_nuclear_and_gas_api
    dataset = api.get_all_company_nuclear_and_gas_data(company_id=company_id)

    return dataset


def _get_data_id_by_year_(company_id: str, year: str) -> str:
    dataset = _get_all_company_datasets_(company_id=company_id)
    # Eintragen aus welcher Periode man das Dataset haben will -> In diesem Fall 2024
    data_id = "test"
    for t in range(len(dataset)):
        if dataset[t].meta_info.reporting_period == year:
            data_id = dataset[t].meta_info.data_id
            break

    return data_id


def _get_dataset_by_year_(company_id: str, year: str) -> CompanyAssociatedDataNuclearAndGasData:
    data_id = _get_data_id_by_year_(company_id=company_id, year=year)
    data = dataland_client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(data_id=data_id)
    return data


def _get_value1_by_year_(company_id: str, year: str) -> str:
    data = _get_dataset_by_year_(company_id=company_id, year=year)
    value1 = data.data.general.general.nuclear_energy_related_activities_section426.value.value
    return value1


def _get_datasource_reference_bytes_(company_id: str, year: str) -> str:
    data = _get_dataset_by_year_(company_id=company_id, year=year)
    value1 = data.data.general.general.nuclear_energy_related_activities_section426
    document_bytes = dataland_client.documents_api.get_document(value1.data_source.file_reference)
    return document_bytes
