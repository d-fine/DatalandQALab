from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_backend.models.yes_no import YesNo


def get_yes_no_values_by_data(data: NuclearAndGasData) -> dict[str, YesNo | None]:
    """Get Yes/No values of the given dataset as a dictionary with section names as keys."""
    data = data.general.general
    sections = {
        "nuclear_energy_related_activities_section426": data.nuclear_energy_related_activities_section426,
        "nuclear_energy_related_activities_section427": data.nuclear_energy_related_activities_section427,
        "nuclear_energy_related_activities_section428": data.nuclear_energy_related_activities_section428,
        "fossil_gas_related_activities_section429": data.fossil_gas_related_activities_section429,
        "fossil_gas_related_activities_section430": data.fossil_gas_related_activities_section430,
        "fossil_gas_related_activities_section431": data.fossil_gas_related_activities_section431,
    }
    section_values = {
        key: (section.value if section is not None and section.value is not None else None)
        for key, section in sections.items()
    }
    return section_values


def get_datasources_of_nuclear_and_gas_yes_no_questions(
    data: NuclearAndGasData,
) -> dict[str, ExtendedDocumentReference | None]:
    """Get list of extended document references from given dataset."""
    data = data.general.general
    sections = {
        "nuclear_energy_related_activities_section426": data.nuclear_energy_related_activities_section426,
        "nuclear_energy_related_activities_section427": data.nuclear_energy_related_activities_section427,
        "nuclear_energy_related_activities_section428": data.nuclear_energy_related_activities_section428,
        "fossil_gas_related_activities_section429": data.fossil_gas_related_activities_section429,
        "fossil_gas_related_activities_section430": data.fossil_gas_related_activities_section430,
        "fossil_gas_related_activities_section431": data.fossil_gas_related_activities_section431,
    }
    section_values = {
        key: section.data_source if section is not None and section.data_source is not None else None
        for key, section in sections.items()
    }

    return section_values


def get_datasources_of_nuclear_and_gas_numeric_values(
    data: NuclearAndGasData,
) -> dict[str, ExtendedDocumentReference | None]:
    """Get list of extended document references from given dataset."""
    data = data.general

    sections = {
        "capex_denominator": data.taxonomy_aligned_denominator.nuclear_and_gas_taxonomy_aligned_capex_denominator,
        "revenue_denominator": data.taxonomy_aligned_denominator.nuclear_and_gas_taxonomy_aligned_revenue_denominator,
        "capex_numerator": data.taxonomy_aligned_numerator.nuclear_and_gas_taxonomy_aligned_capex_numerator,
        "revenue_numerator": data.taxonomy_aligned_numerator.nuclear_and_gas_taxonomy_aligned_revenue_numerator,
        "not_aligned_capex": (
            data.taxonomy_eligible_but_not_aligned.nuclear_and_gas_taxonomy_eligible_but_not_aligned_capex
        ),
        "not_aligned_revenue": (
            data.taxonomy_eligible_but_not_aligned.nuclear_and_gas_taxonomy_eligible_but_not_aligned_revenue
        ),
        "non_eligible_capex": data.taxonomy_non_eligible.nuclear_and_gas_taxonomy_non_eligible_capex,
        "non_eligible_revenue": data.taxonomy_non_eligible.nuclear_and_gas_taxonomy_non_eligible_revenue,
    }
    datasource_list = {
        key: (section.data_source if section is not None and section.data_source is not None else None)
        for key, section in sections.items()
    }
    return datasource_list
