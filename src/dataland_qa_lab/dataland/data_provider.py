from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
from dataland_backend.models.nuclear_and_gas_aligned_denominator import NuclearAndGasAlignedDenominator
from dataland_backend.models.nuclear_and_gas_aligned_numerator import NuclearAndGasAlignedNumerator
from dataland_backend.models.nuclear_and_gas_eligible_but_not_aligned import NuclearAndGasEligibleButNotAligned
from dataland_backend.models.nuclear_and_gas_non_eligible import NuclearAndGasNonEligible
from dataland_backend.models.yes_no import YesNo

from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def get_yes_no_values_by_data(data: NuclearAndGasDataCollection) -> dict[str, YesNo | None]:
    """Get Yes/No values of the given dataset as a dictionary with section names as keys."""
    sections = data.yes_no_data_points

    section_values = {
        key: (data.datapoint.value if data and data.datapoint and data.datapoint.value is not None else None)
        for key, data in sections.items()
    }
    return section_values


def get_taxonomy_aligned_revenue_denominator_values_by_data(data: NuclearAndGasDataCollection) -> dict:
    """Retrieve taxonomy-aligned revenue denominator values from the dataset."""
    denominator_values_dict = {}
    try:
        denominator_values = (
            data.taxonomy_aligned_denominator
            .get("taxonomy_aligned_revenue_denominator")
            .datapoint.value
        )
        for field_name in NuclearAndGasAlignedDenominator.model_fields:
            denominator_values_dict[field_name] = extract_field_data(denominator_values, field_name)
    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error processing taxonomy-aligned revenue denominator: {e}")

    return denominator_values_dict

def get_taxonomy_aligned_capex_denominator_values_by_data(data: NuclearAndGasDataCollection) -> dict:
    """Retrieve taxonomy-aligned capex denominator values from the dataset."""
    denominator_values_dict = {}
    try:
        denominator_values = (
            data.taxonomy_aligned_denominator
            .get("taxonomy_aligned_capex_denominator")
            .datapoint.value
        )
        for field_name in NuclearAndGasAlignedDenominator.model_fields:
            denominator_values_dict[field_name] = extract_field_data(denominator_values, field_name)
    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error processing taxonomy-aligned capex denominator: {e}")

    return denominator_values_dict


def get_taxonomy_aligned_revenue_numerator_values_by_data(data: NuclearAndGasDataCollection) -> dict:
    """Retrieve taxonomy-aligned revenue numerator values from the dataset."""
    numerator_values_dict = {}
    try:
        numerator_values = (
            data.taxonomy_aligned_numerator
            .get("taxonomy_aligned_revenue_numerator")
            .datapoint.value
        )
        for field_name in NuclearAndGasAlignedNumerator.model_fields:
            numerator_values_dict[field_name] = extract_field_data(numerator_values, field_name)
    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error processing taxonomy-aligned revenue numerator: {e}")

    return numerator_values_dict


def get_taxonomy_aligned_capex_numerator_values_by_data(data: NuclearAndGasDataCollection) -> dict:
    """Retrieve taxonomy-aligned capex numerator values from the dataset."""
    numerator_values_dict = {}
    try:
        numerator_values = (
            data.taxonomy_aligned_numerator
            .get("taxonomy_aligned_capex_numerator")
            .datapoint.value
        )
        for field_name in NuclearAndGasAlignedNumerator.model_fields:
            numerator_values_dict[field_name] = extract_field_data(numerator_values, field_name)
    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error processing taxonomy-aligned capex numerator: {e}")

    return numerator_values_dict

def get_taxonomy_eligible_but_not_aligned_revenue_values_by_data(data: NuclearAndGasDataCollection) -> dict:
    """Retrieve taxonomy eligible but not aligned revenue numerator values from the dataset."""
    eligible_but_not_aligned_dict = {}
    try:
        eligible_values = (
            data.taxonomy_eligble_but_not_aligned
            .get("taxonomy_not_aligned_revenue")
            .datapoint.value
        )
        for field_name in NuclearAndGasEligibleButNotAligned.model_fields:
            eligible_but_not_aligned_dict[field_name] = extract_field_data(eligible_values, field_name)
    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error processing taxonomy eligible but not aligned revenue: {e}")

    return eligible_but_not_aligned_dict

def get_taxonomy_eligible_but_not_aligned_capex_values_by_data(data: NuclearAndGasDataCollection) -> dict:
    """Retrieve taxonomy eligible but not aligned capex from the dataset."""
    eligible_but_not_aligned_dict = {}
    try:
        eligible_values = (
            data.taxonomy_eligble_but_not_aligned
            .get("taxonomy_not_aligned_capex")
            .datapoint.value
        )
        for field_name in NuclearAndGasEligibleButNotAligned.model_fields:
            eligible_but_not_aligned_dict[field_name] = extract_field_data(eligible_values, field_name)
    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error processing taxonomy eligible but not aligned capex: {e}")

    return eligible_but_not_aligned_dict

def get_taxonomy_non_eligible_revenue_values_by_data(data: NuclearAndGasDataCollection) -> dict:
    """Retrieve taxonomy non-eligible revenue numerator values from the dataset."""
    non_eligible_dict = {}
    try:
        non_eligible_values = (
            data.taxonomy_non_eligible
            .get("taxonomy_non_eligible_revenue")
            .datapoint.value
        )
        for field_name in NuclearAndGasNonEligible.model_fields:
            value = getattr(non_eligible_values, field_name, None)
            non_eligible_dict[field_name] = -1 if value is None else value
    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error processing taxonomy non-eligible revenue: {e}")

    return non_eligible_dict

def get_taxonomy_non_eligible_capex_values_by_data(data: NuclearAndGasDataCollection) -> dict:
    """Retrieve taxonomy non-eligible capex numerator values from the dataset."""
    non_eligible_dict = {}
    try:
        non_eligible_values = (
            data.taxonomy_non_eligible
            .get("taxonomy_non_eligible_capex")
            .datapoint.value
        )
        for field_name in NuclearAndGasNonEligible.model_fields:
            value = getattr(non_eligible_values, field_name, None)
            non_eligible_dict[field_name] = -1 if value is None else value
    except (AttributeError, KeyError, TypeError) as e:
        print(f"Error processing taxonomy non-eligible capex: {e}")

    return non_eligible_dict

def extract_field_data(values: any, field_name: str) -> list:
    """Extract mitigation, adaptation, and mitigationAndAdaptation values from a field and return them as a list."""
    field_value = getattr(values, field_name, None)

    value = getattr(field_value, "mitigation_and_adaptation", None)
    mitigation_and_adaptation = -1 if value is None else value
    value = getattr(field_value, "mitigation", None)
    mitigation = -1 if value is None else value
    value = getattr(field_value, "adaptation", None)
    adaptation = -1 if value is None else value

    return [mitigation_and_adaptation, mitigation, adaptation]


def get_datasources_of_nuclear_and_gas_yes_no_questions(
    data: NuclearAndGasDataCollection,
) -> dict[str, ExtendedDocumentReference | None]:
    """Get list of extended document references from given dataset."""
    sections = data.yes_no_data_points

    section_values = {
        key: (
            section.datapoint.data_source
            if section and section.datapoint and section.datapoint.data_source is not None
            else None
        )
        for key, section in sections.items()
    }

    return section_values


def get_datasources_of_nuclear_and_gas_numeric_values(
    data: NuclearAndGasDataCollection,
) -> dict[str, ExtendedDocumentReference | None]:
    """Get list of extended document references from given dataset."""
    sections = {
        "taxonomy_aligned_denominator": data.taxonomy_aligned_denominator,
        "taxonomy_aligned_numerator": data.taxonomy_aligned_numerator,
        "taxonomy_eligble_but_not_aligned": data.taxonomy_eligble_but_not_aligned,
        "taxonomy_non_eligible": data.taxonomy_non_eligible,
    }

    section_list = {
        key: data_source for section in sections.values() for key, data_source in extract_data_source(section).items()
    }

    return section_list


def extract_data_source(section: dict[str, any]) -> dict[str, ExtendedDocumentReference]:
    """Extract datasource for each data point."""
    return (
        {
            key: (
                subsection.datapoint.data_source
                if subsection is not None
                and subsection.datapoint is not None
                and subsection.datapoint.data_source is not None
                else None
            )
            for key, subsection in section.items()
        }
        if section is not None
        else None
    )
