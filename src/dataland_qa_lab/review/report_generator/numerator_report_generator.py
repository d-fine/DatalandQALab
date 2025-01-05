from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.extended_data_point_nuclear_and_gas_aligned_numerator import (
    ExtendedDataPointNuclearAndGasAlignedNumerator,
)
from dataland_qa.models.extended_document_reference import ExtendedDocumentReference
from dataland_qa.models.nuclear_and_gas_aligned_numerator import NuclearAndGasAlignedNumerator
from dataland_qa.models.nuclear_and_gas_environmental_objective import NuclearAndGasEnvironmentalObjective
from dataland_qa.models.nuclear_and_gas_general_taxonomy_aligned_numerator import (
    NuclearAndGasGeneralTaxonomyAlignedNumerator,
)
from dataland_qa.models.qa_report_data_point_extended_data_point_nuclear_and_gas_aligned_numerator import (
    QaReportDataPointExtendedDataPointNuclearAndGasAlignedNumerator,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review.numeric_value_generator import NumericValueGenerator
from dataland_qa_lab.utils.doc_ref_to_qa_ref_mapper import map_doc_ref_to_qa_doc_ref
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def build_taxonomy_aligned_numerator_report(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult
) -> NuclearAndGasGeneralTaxonomyAlignedNumerator:
    """Create Report Frame for the Nuclear and Gas General Taxonomy Aligned Numerator."""
    return NuclearAndGasGeneralTaxonomyAlignedNumerator(
        nuclearAndGasTaxonomyAlignedRevenueNumerator=build_numerator_report_frame(dataset, relevant_pages, "Revenue"),
        nuclearAndGasTaxonomyAlignedCapexNumerator=build_numerator_report_frame(dataset, relevant_pages, "CapEx")
    )


def build_numerator_report_frame(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult, kpi: str
) -> QaReportDataPointExtendedDataPointNuclearAndGasAlignedNumerator:
    """Build report frame for the revenue Numerator."""
    aligned_numerator, verdict, comment = compare_numerator_values(dataset, relevant_pages, kpi)

    return QaReportDataPointExtendedDataPointNuclearAndGasAlignedNumerator(
        comment=comment,
        verdict=verdict,
        correctedData=ExtendedDataPointNuclearAndGasAlignedNumerator(
            value=aligned_numerator,
            quality="Incomplete",
            comment=comment,
            dataSource=get_data_source(dataset),
        ),
    )


def compare_numerator_values(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult, kpi: str
) -> tuple[NuclearAndGasAlignedNumerator, QaReportDataPointVerdict, str]:
    """Compare Numerator values and return results."""
    numerator_values = NumericValueGenerator.get_taxonomy_alligned_numerator(relevant_pages, kpi)
    dataland_numeator_values = None
    if (kpi == "Revenue"):
        dataland_numeator_values = data_provider.get_taxonomy_aligned_revenue_numerator_values_by_data(dataset)
    else:
        dataland_numeator_values = data_provider.get_taxonomy_aligned_capex_numerator_values_by_data(dataset)
    aligned_numerator = NuclearAndGasAlignedNumerator()
    verdict = QaReportDataPointVerdict.QAACCEPTED
    comment = ""
    current_index = 0

    for field_name, dataland_value_list in dataland_numeator_values.items():
        # Extract the corresponding slice from dominator_values
        prompt_value_list = numerator_values[current_index : current_index + 3]
        correct_value_list = dataland_value_list
        if dataland_value_list != prompt_value_list:
            verdict = QaReportDataPointVerdict.QAREJECTED
            discrepancies = ", ".join(
                f"{v1} != {v2}" for v1, v2 in zip(dataland_value_list, prompt_value_list, strict=False) if v1 != v2
            )
            comment += f" Discrepancy in '{field_name}': {discrepancies}."

        setattr(
            aligned_numerator,
            field_name,
            NuclearAndGasEnvironmentalObjective(
                mitigationAndAdaptation=correct_value_list[0],
                mitigation=correct_value_list[1],
                adaptation=correct_value_list[2],
            ),
        )
        # Update the current index for the next slice
        current_index += 3

    return aligned_numerator, verdict, comment


def get_data_source(dataset: NuclearAndGasDataCollection) -> ExtendedDocumentReference | None:
    """Retrieve the data source mapped to a QA document reference."""
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_numeric_values(data=dataset)
    data_source = data_sources.get("taxonomy_aligned_numerator")
    return map_doc_ref_to_qa_doc_ref(data_source)
