from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData


class DataProvider:
    """Provide certain data from Nuclear and Gas datasets."""

    @classmethod
    def get_yes_no_values_by_data(cls, data: NuclearAndGasData) -> list[str]:
        """Get Yes/No values of given dataset."""
        referenced_reports = data.general.general
        sections = [
            referenced_reports.nuclear_energy_related_activities_section426,
            referenced_reports.nuclear_energy_related_activities_section427,
            referenced_reports.nuclear_energy_related_activities_section428,
            referenced_reports.fossil_gas_related_activities_section429,
            referenced_reports.fossil_gas_related_activities_section430,
            referenced_reports.fossil_gas_related_activities_section431
        ]

        document_value_list = [
            section.value
            if section is not None and section.value is not None else None
            for section in sections
        ]

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