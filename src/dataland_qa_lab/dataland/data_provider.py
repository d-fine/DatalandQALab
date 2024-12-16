from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
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
        identifier: data_source
        for section in sections.values()
        for identifier, data_source in extract_data_source(section).items()
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
