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
        nuclearAndGasTaxonomyAlignedCapexNumerator=build_numerator_report_frame(dataset, relevant_pages, "CapEx"),
    )


def build_numerator_report_frame(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult, kpi: str
) -> QaReportDataPointExtendedDataPointNuclearAndGasAlignedNumerator:
    """Build report frame for the revenue Numerator."""
    aligned_numerator, verdict, comment = compare_numerator_values(dataset, relevant_pages, kpi)

    corrected_data = (
        ExtendedDataPointNuclearAndGasAlignedNumerator(
            value=aligned_numerator,
            quality="Incomplete",
            comment=comment,
            dataSource=get_data_source(dataset),
        )
        if verdict != QaReportDataPointVerdict.QAACCEPTED
        else ExtendedDataPointNuclearAndGasAlignedNumerator()
    )

    return QaReportDataPointExtendedDataPointNuclearAndGasAlignedNumerator(
        comment=comment,
        verdict=verdict,
        correctedData=corrected_data
    )


def compare_numerator_values(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult, kpi: str
) -> tuple[NuclearAndGasAlignedNumerator, QaReportDataPointVerdict, str]:
    """Compare Numerator values and return results."""
    # Generate prompted values and split them into chunks
    prompted_values = NumericValueGenerator.get_taxonomy_alligned_numerator(relevant_pages, kpi)
    chunked_prompted_values = [prompted_values[i : i + 3] for i in range(0, len(prompted_values), 3)]

    dataland_values = get_dataland_values(dataset, kpi)

    aligned_numerator = None
    verdict = QaReportDataPointVerdict.QAACCEPTED
    comments = []

    for (field_name, dataland_vals), prompt_vals in zip(dataland_values.items(), chunked_prompted_values, strict=False):
        if dataland_vals != prompt_vals:
            verdict = QaReportDataPointVerdict.QAREJECTED
            discrepancies = generate_discrepancies(dataland_vals, prompt_vals)
            comments.append(f"Discrepancy in '{field_name}': {discrepancies}.")
            aligned_numerator = (
                NuclearAndGasAlignedNumerator() if aligned_numerator is None else aligned_numerator
            )
            update_attribute(aligned_numerator, field_name, prompt_vals)

    return aligned_numerator, verdict, "".join(comments)


def get_dataland_values(dataset: NuclearAndGasDataCollection, kpi: str) -> dict:
    """Retrieve dataland Numerator values based on KPI."""
    if kpi == "Revenue":
        return data_provider.get_taxonomy_aligned_revenue_numerator_values_by_data(dataset)
    return data_provider.get_taxonomy_aligned_capex_numerator_values_by_data(dataset)


def generate_discrepancies(dataland_values: list, prompted_values: list) -> str:
    """Generate a string describing discrepancies between two lists of values."""
    return ", ".join(f"{v1} != {v2}" for v1, v2 in zip(dataland_values, prompted_values, strict=False) if v1 != v2)


def update_attribute(obj: NuclearAndGasAlignedNumerator, field_name: str, values: list) -> None:
    """Set an attribute of the aligned Numerator by field name."""
    setattr(
        obj,
        field_name,
        NuclearAndGasEnvironmentalObjective(
            mitigationAndAdaptation=values[0],
            mitigation=values[1],
            adaptation=values[2],
        ),
    )


def get_data_source(dataset: NuclearAndGasDataCollection) -> ExtendedDocumentReference | None:
    """Retrieve the data source mapped to a QA document reference."""
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_numeric_values(data=dataset)
    data_source = data_sources.get("taxonomy_aligned_numerator")
    return map_doc_ref_to_qa_doc_ref(data_source)
