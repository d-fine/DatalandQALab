from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.extended_data_point_nuclear_and_gas_aligned_denominator import (
    ExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_qa.models.extended_document_reference import ExtendedDocumentReference
from dataland_qa.models.nuclear_and_gas_aligned_denominator import NuclearAndGasAlignedDenominator
from dataland_qa.models.nuclear_and_gas_environmental_objective import NuclearAndGasEnvironmentalObjective
from dataland_qa.models.nuclear_and_gas_general_taxonomy_aligned_denominator import (
    NuclearAndGasGeneralTaxonomyAlignedDenominator,
)
from dataland_qa.models.qa_report_data_point_extended_data_point_nuclear_and_gas_aligned_denominator import (
    QaReportDataPointExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review.numeric_value_generator import NumericValueGenerator
from dataland_qa_lab.utils.doc_ref_to_qa_ref_mapper import map_doc_ref_to_qa_doc_ref
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def build_taxonomy_aligned_denominator_report(
    dataset: NuclearAndGasDataCollection,
    relevant_pages: AnalyzeResult
) -> NuclearAndGasGeneralTaxonomyAlignedDenominator:
    """Create Report Frame for the Nuclear and Gas General Taxonomy Aligned Denominator."""
    return NuclearAndGasGeneralTaxonomyAlignedDenominator(
        nuclearAndGasTaxonomyAlignedRevenueDenominator=build_revenue_denominator_report_frame(dataset, relevant_pages),
    )


def build_revenue_denominator_report_frame(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult
) -> QaReportDataPointExtendedDataPointNuclearAndGasAlignedDenominator:
    """Build report frame for the revenue denominator."""
    aligned_denominator, verdict, comment = compare_denominator_values(dataset, relevant_pages)

    return QaReportDataPointExtendedDataPointNuclearAndGasAlignedDenominator(
        comment=comment,
        verdict=verdict,
        correctedData=ExtendedDataPointNuclearAndGasAlignedDenominator(
            value=aligned_denominator,
            quality="Incomplete",
            comment=comment,
            dataSource=get_data_source(dataset),
        ),
    )


def compare_denominator_values(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult
) -> tuple[NuclearAndGasAlignedDenominator, QaReportDataPointVerdict, str]:
    """Compare denominator values and return results."""
    dominator_values = NumericValueGenerator.get_taxonomy_alligned_denominator(relevant_pages)
    dataland_dominator_values = data_provider.get_taxonomy_aligned_revenue_denominator_values_by_data(dataset)

    aligned_denominator = NuclearAndGasAlignedDenominator()
    verdict = QaReportDataPointVerdict.QAACCEPTED
    comment = ""
    current_index = 0

    for field_name, value_list in dataland_dominator_values.items():
        # Extract the corresponding slice from dominator_values
        comparison_slice = dominator_values[current_index : current_index + 3]

        if value_list != comparison_slice:
            verdict = QaReportDataPointVerdict.QAREJECTED
            discrepancies = ", ".join(
                f"{v1} != {v2}" for v1, v2 in zip(value_list, comparison_slice, strict=False) if v1 != v2
            )
            comment += f" Discrepancy in '{field_name}': {discrepancies}."

        setattr(
            aligned_denominator,
            field_name,
            NuclearAndGasEnvironmentalObjective(
                mitigationAndAdaptation=comparison_slice[0],
                mitigation=comparison_slice[1],
                adaptation=comparison_slice[2],
            ),
        )
        # Update the current index for the next slice
        current_index += 3

    return aligned_denominator, verdict, comment


def get_data_source(dataset: NuclearAndGasDataCollection) -> ExtendedDocumentReference | None:
    """Retrieve the data source mapped to a QA document reference."""
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_numeric_values(data=dataset)
    data_source = data_sources.get("taxonomy_aligned_denominator")
    return map_doc_ref_to_qa_doc_ref(data_source)
