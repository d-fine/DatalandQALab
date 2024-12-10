from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_backend.models.yes_no import YesNo


def get_yes_no_values_by_data(data: NuclearAndGasData) -> list[YesNo | None]:
    """Get Yes/No values of given dataset."""
    general_data_points = data.general.general
    sections = [
        general_data_points.nuclear_energy_related_activities_section426,
        general_data_points.nuclear_energy_related_activities_section427,
        general_data_points.nuclear_energy_related_activities_section428,
        general_data_points.fossil_gas_related_activities_section429,
        general_data_points.fossil_gas_related_activities_section430,
        general_data_points.fossil_gas_related_activities_section431,
    ]
    document_value_list = [
        section.value if section is not None and section.value is not None else None for section in sections
    ]
    return document_value_list


def get_datasources_of_nuclear_and_gas_yes_no_questions(
    data: NuclearAndGasData,
) -> list[ExtendedDocumentReference | None]:
    """Get list of extended document references from given dataset."""
    referenced_reports = data.general.general
    sections = [
        referenced_reports.nuclear_energy_related_activities_section426,
        referenced_reports.nuclear_energy_related_activities_section427,
        referenced_reports.nuclear_energy_related_activities_section428,
        referenced_reports.fossil_gas_related_activities_section429,
        referenced_reports.fossil_gas_related_activities_section430,
        referenced_reports.fossil_gas_related_activities_section431,
    ]
    datasource_list = [
        section.data_source if section is not None and section.data_source is not None else None for section in sections
    ]
    return datasource_list


def get_datasources_of_nuclear_and_gas_numeric_values(
    data: NuclearAndGasData,
) -> list[ExtendedDocumentReference | None]:
    """Get list of extended document references from given dataset."""
    sections = [
        data.general.taxonomy_aligned_denominator.nuclear_and_gas_taxonomy_aligned_capex_denominator,
        data.general.taxonomy_aligned_denominator.nuclear_and_gas_taxonomy_aligned_revenue_denominator,
        data.general.taxonomy_aligned_numerator.nuclear_and_gas_taxonomy_aligned_capex_numerator,
        data.general.taxonomy_aligned_numerator.nuclear_and_gas_taxonomy_aligned_revenue_numerator,
        data.general.taxonomy_eligible_but_not_aligned.nuclear_and_gas_taxonomy_eligible_but_not_aligned_capex,
        data.general.taxonomy_eligible_but_not_aligned.nuclear_and_gas_taxonomy_eligible_but_not_aligned_revenue,
        data.general.taxonomy_non_eligible.nuclear_and_gas_taxonomy_non_eligible_capex,
        data.general.taxonomy_non_eligible.nuclear_and_gas_taxonomy_non_eligible_revenue,
    ]
    datasource_list = [
        section.data_source if section is not None and section.data_source is not None else None for section in sections
    ]
    return datasource_list
