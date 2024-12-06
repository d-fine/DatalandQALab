from dataland_backend.models.company_associated_data_nuclear_and_gas_data import CompanyAssociatedDataNuclearAndGasData
from dataland_backend.models.extended_document_reference import ExtendedDocumentReference

from dataland_qa_lab.utils import config


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
    data: CompanyAssociatedDataNuclearAndGasData,
) -> list[ExtendedDocumentReference | None]:
    """Get list of data references in bytes from given dataset."""
    referenced_reports = data.data.general.general
    document_byte_list = []

    document_byte_list.extend(
        (
            referenced_reports.nuclear_energy_related_activities_section426.data_source,
            referenced_reports.nuclear_energy_related_activities_section427.data_source,
            referenced_reports.nuclear_energy_related_activities_section428.data_source,
            referenced_reports.fossil_gas_related_activities_section429.data_source,
            referenced_reports.fossil_gas_related_activities_section430.data_source,
            referenced_reports.fossil_gas_related_activities_section431.data_source,
        )
    )
    return document_byte_list


def get_data_id_by_company_id(company_id: str) -> str:
    """Get data id using company id."""
    client = config.get_config().dataland_client
    datasets = client.eu_taxonomy_nuclear_and_gas_api.get_all_company_nuclear_and_gas_data(company_id=company_id)
    return datasets[0].meta_info.data_id
