from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
from dataland_qa.models.nuclear_and_gas_data import NuclearAndGasData


class DataProvider:
    """Provide certain data from Nuclear and Gas datasets."""

    @classmethod
    def get_values_by_data(cls, data: NuclearAndGasData) -> list[str]:
        """Get Yes/No values of given dataset."""
        referenced_reports = data.general.general
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

    @classmethod
    def get_datasources_of_data_points(
        cls,
        data: NuclearAndGasData,
    ) -> list[ExtendedDocumentReference | None]:
        """Get list of data references in bytes from given dataset."""
        referenced_reports = data.general.general
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
