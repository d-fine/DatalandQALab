import logging

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.extended_data_point_nuclear_and_gas_aligned_denominator import (
    ExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_qa.models.extended_document_reference import ExtendedDocumentReference
from dataland_qa.models.nuclear_and_gas_aligned_denominator import NuclearAndGasAlignedDenominator
from dataland_qa.models.nuclear_and_gas_general_taxonomy_aligned_denominator import (
    NuclearAndGasGeneralTaxonomyAlignedDenominator,
)
from dataland_qa.models.qa_report_data_point_extended_data_point_nuclear_and_gas_aligned_denominator import (
    QaReportDataPointExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review.numeric_value_generator import NumericValueGenerator
from dataland_qa_lab.utils import comparator
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def build_taxonomy_aligned_denominator_report(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult
) -> NuclearAndGasGeneralTaxonomyAlignedDenominator:
    """Create a report frame for the Nuclear and Gas General Taxonomy Aligned Denominator."""
    return NuclearAndGasGeneralTaxonomyAlignedDenominator(
        nuclearAndGasTaxonomyAlignedRevenueDenominator=build_denominator_report_frame(
            dataset, relevant_pages, "Revenue"
        ),
        nuclearAndGasTaxonomyAlignedCapexDenominator=build_denominator_report_frame(dataset, relevant_pages, "CapEx"),
    )


def build_denominator_report_frame(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult, kpi: str
) -> QaReportDataPointExtendedDataPointNuclearAndGasAlignedDenominator:
    """Build a report frame for a specific KPI denominator (Revenue or CapEx)."""
    prompted_values = NumericValueGenerator.get_taxonomy_alligned_denominator(relevant_pages, kpi)
    dataland_values = get_dataland_values(dataset, kpi)

    corrected_values, verdict, comment, quality = comparator.compare_values_template_2to4(
        prompted_values, dataland_values, NuclearAndGasAlignedDenominator
    )

    if verdict == QaReportDataPointVerdict.QAACCEPTED:
        corrected_data = ExtendedDataPointNuclearAndGasAlignedDenominator()  # left empty if no corrections are made
    else:
        corrected_data = ExtendedDataPointNuclearAndGasAlignedDenominator(
            value=corrected_values,
            quality=quality,
            comment="",
            dataSource=get_data_source(dataset),
        )

    return QaReportDataPointExtendedDataPointNuclearAndGasAlignedDenominator(
        comment=comment,
        verdict=verdict,
        correctedData=corrected_data,
    )


def get_dataland_values(dataset: NuclearAndGasDataCollection, kpi: str) -> dict:
    """Retrieve dataland denominator values based on KPI."""
    if kpi == "Revenue":
        data = data_provider.get_taxonomy_aligned_revenue_denominator_values_by_data(dataset)
    else:
        data = data_provider.get_taxonomy_aligned_capex_denominator_values_by_data(dataset)

    if data is None:
        logging.error("Retrieved data is None for KPI: %s", kpi)

    return data


def get_data_source(dataset: NuclearAndGasDataCollection) -> ExtendedDocumentReference | None:
    """Retrieve the data source mapped to a QA document reference."""
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_numeric_values(data=dataset)
    data_source = data_sources.get("taxonomy_aligned_denominator")
    return comparator.map_doc_ref_to_qa_doc_ref(data_source)
