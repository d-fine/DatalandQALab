import logging

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
    """Build a report frame for a specific KPI numerator (Revenue or CapEx)."""
    prompted_values = NumericValueGenerator.get_taxonomy_alligned_numerator(relevant_pages, kpi)
    dataland_values = get_dataland_values(dataset, kpi)

    corrected_values, verdict, comment, quality = compare_numerator_values(prompted_values, dataland_values)
    if verdict == QaReportDataPointVerdict.QAACCEPTED:
        corrected_data = ExtendedDataPointNuclearAndGasAlignedNumerator()
    else:
        corrected_data = ExtendedDataPointNuclearAndGasAlignedNumerator(
            value=corrected_values,
            quality=quality,
            comment=comment,
            dataSource=get_data_source(dataset),
        )
    return QaReportDataPointExtendedDataPointNuclearAndGasAlignedNumerator(
        comment=comment,
        verdict=verdict,
        correctedData=corrected_data
    )


def compare_numerator_values(
    prompted_values: list, dataland_values: dict
) -> tuple[NuclearAndGasAlignedNumerator, QaReportDataPointVerdict, str, str]:
    """Compare denominator values from the dataset with the prompted values."""
    chunked_prompt_vals = [prompted_values[i : i + 3] for i in range(0, len(prompted_values), 3)]
    corrected_values = NuclearAndGasAlignedNumerator()
    verdict = QaReportDataPointVerdict.QAACCEPTED
    quality = "Reported"
    comments = []

    for (field_name, dataland_vals), prompt_vals in zip(dataland_values.items(), chunked_prompt_vals, strict=False):
        for prompt_val, dataland_val in zip(prompt_vals, dataland_vals, strict=False):
            if prompt_val == -1 and dataland_val != -1:  # Prompt did not contain a value
                quality = "NoDataFound"
                verdict = QaReportDataPointVerdict.QAINCONCLUSIVE
                comments.append(f"No Data found for '{field_name}': {dataland_val} != {prompt_val}.")
            elif prompt_val != dataland_val:
                verdict = QaReportDataPointVerdict.QAREJECTED
                comments.append(f"Discrepancy in '{field_name}': {dataland_val} != {prompt_val}.")
        update_attribute(corrected_values, field_name, prompt_vals)

    return corrected_values, verdict, "".join(comments), quality


def get_dataland_values(dataset: NuclearAndGasDataCollection, kpi: str) -> dict:
    """Retrieve dataland numerator values based on KPI."""
    if kpi == "Revenue":
        data = data_provider.get_taxonomy_aligned_revenue_numerator_values_by_data(dataset)
    else:
        data = data_provider.get_taxonomy_aligned_capex_numerator_values_by_data(dataset)

    if data is None:
        logging.error("Retrieved data is None for KPI: %s", kpi)

    return data


def update_attribute(obj: NuclearAndGasAlignedNumerator, field_name: str, values: list) -> None:
    """Set an attribute of the aligned numerator by field name."""
    # Replace -1 with None in the values list
    values = [None if v == -1 else v for v in values]
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
