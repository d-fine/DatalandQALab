from dataland_backend.models.company_associated_data_nuclear_and_gas_data import CompanyAssociatedDataNuclearAndGasData

from dataland_qa_lab.dataland.dataland_client import DatalandClient


def get_all_company_datasets(company_id: str, dataland_client: DatalandClient) -> str:
    """Get all datasets of a certain company."""
    api = dataland_client.eu_taxonomy_nuclear_and_gas_api
    datasets = api.get_all_company_nuclear_and_gas_data(company_id=company_id)

    return datasets


def get_data_id_by_year(company_id: str, year: str, dataland_client: DatalandClient) -> str:
    """Get Data_ID of given company within wanted period."""
    dataset = get_all_company_datasets(company_id=company_id, dataland_client=dataland_client)
    data_id = ""
    for t in range(len(dataset)):
        if dataset[t].meta_info.reporting_period == year:
            data_id = dataset[t].meta_info.data_id
            break

    return data_id


def get_data_by_data_id(data_id: str, dataland_client: DatalandClient) -> CompanyAssociatedDataNuclearAndGasData:
    """Get certain dataset with data_id."""
    data = dataland_client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(data_id=data_id)
    return data


def get_values_by_data(data: CompanyAssociatedDataNuclearAndGasData) -> list[str]:
    """Get Yes/No values of given dataset."""
    referenced_reports = data.data.general.general
    document_value_list = []

    document_value_list.extend(
        (
            referenced_reports.nuclear_energy_related_activities_section426.value.value
            if referenced_reports.nuclear_energy_related_activities_section426.value is not None
            else None,
            referenced_reports.nuclear_energy_related_activities_section427.value.value
            if referenced_reports.nuclear_energy_related_activities_section427.value is not None
            else None,
            referenced_reports.nuclear_energy_related_activities_section428.value.value
            if referenced_reports.nuclear_energy_related_activities_section428.value is not None
            else None,
            referenced_reports.fossil_gas_related_activities_section429.value.value
            if referenced_reports.fossil_gas_related_activities_section429.value is not None
            else None,
            referenced_reports.fossil_gas_related_activities_section430.value.value
            if referenced_reports.fossil_gas_related_activities_section430.value is not None
            else None,
            referenced_reports.fossil_gas_related_activities_section431.value.value
            if referenced_reports.fossil_gas_related_activities_section431.value is not None
            else None,
        )
    )
    return document_value_list


def get_datasource_reference_bytes(
    data: CompanyAssociatedDataNuclearAndGasData, dataland_client: DatalandClient
) -> list[bytearray]:
    """Get list of data references in bytes from given dataset."""
    referenced_reports = data.data.general.general
    document_byte_list = []

    document_byte_list.extend(
        (
            dataland_client.documents_api.get_document(
                referenced_reports.nuclear_energy_related_activities_section426.data_source.file_reference
            ),
            dataland_client.documents_api.get_document(
                referenced_reports.nuclear_energy_related_activities_section427.data_source.file_reference
            ),
            dataland_client.documents_api.get_document(
                referenced_reports.nuclear_energy_related_activities_section428.data_source.file_reference
            ),
            dataland_client.documents_api.get_document(
                referenced_reports.fossil_gas_related_activities_section429.data_source.file_reference
            ),
            dataland_client.documents_api.get_document(
                referenced_reports.fossil_gas_related_activities_section430.data_source.file_reference
            ),
            dataland_client.documents_api.get_document(
                referenced_reports.fossil_gas_related_activities_section431.data_source.file_reference
            ),
        )
    )
    return document_byte_list
