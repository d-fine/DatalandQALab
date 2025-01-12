import logging

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.extended_data_point_nuclear_and_gas_eligible_but_not_aligned import (
    ExtendedDataPointNuclearAndGasEligibleButNotAligned,
)
from dataland_qa.models.extended_document_reference import ExtendedDocumentReference
from dataland_qa.models.nuclear_and_gas_eligible_but_not_aligned import NuclearAndGasEligibleButNotAligned
from dataland_qa.models.nuclear_and_gas_environmental_objective import NuclearAndGasEnvironmentalObjective
from dataland_qa.models.nuclear_and_gas_general_taxonomy_eligible_but_not_aligned import (
    NuclearAndGasGeneralTaxonomyEligibleButNotAligned,
)
from dataland_qa.models.qa_report_data_point_extended_data_point_nuclear_and_gas_eligible_but_not_aligned import (
    QaReportDataPointExtendedDataPointNuclearAndGasEligibleButNotAligned,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review.numeric_value_generator import NumericValueGenerator
from dataland_qa_lab.utils.doc_ref_to_qa_ref_mapper import map_doc_ref_to_qa_doc_ref
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def build_taxonomy_eligible_but_not_aligned_report(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult
) -> NuclearAndGasGeneralTaxonomyEligibleButNotAligned:
    """Create Report Frame for the Nuclear and Gas General Taxonomy eligible but not alinged data."""
    return NuclearAndGasGeneralTaxonomyEligibleButNotAligned(
        nuclearAndGasTaxonomyEligibleButNotAlignedRevenue=build_eligible_but_not_aligned_frame(
            dataset, relevant_pages, "Revenue"
        ),
        nuclearAndGasTaxonomyEligibleButNotAlignedCapex=build_eligible_but_not_aligned_frame(
            dataset, relevant_pages, "CapEx"
        ),
    )


def build_eligible_but_not_aligned_frame(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult, kpi: str
) -> QaReportDataPointExtendedDataPointNuclearAndGasEligibleButNotAligned:
    """Build a report frame for a specific KPI (Revenue or CapEx)."""
    prompted_values = NumericValueGenerator.get_taxonomy_eligible_not_alligned(relevant_pages, kpi)
    dataland_values = get_dataland_values(dataset, kpi)

    corrected_values, verdict, comment, quality = compare_eligible_but_not_aligned_values(
        prompted_values, dataland_values
    )

    if verdict == QaReportDataPointVerdict.QAACCEPTED:
        corrected_data = ExtendedDataPointNuclearAndGasEligibleButNotAligned()
    else:
        corrected_data = ExtendedDataPointNuclearAndGasEligibleButNotAligned(
            value=corrected_values,
            quality=quality,
            comment=comment,
            dataSource=get_data_source(dataset),
        )
    return QaReportDataPointExtendedDataPointNuclearAndGasEligibleButNotAligned(
        comment=comment, verdict=verdict, correctedData=corrected_data
    )


def compare_eligible_but_not_aligned_values(
    prompted_values: list, dataland_values: dict
) -> tuple[NuclearAndGasEligibleButNotAligned, QaReportDataPointVerdict, str, str]:
    """Compare eligible but not aligned values from the dataset with the prompted values."""
    chunked_prompt_vals = [prompted_values[i : i + 3] for i in range(0, len(prompted_values), 3)]
    corrected_values = NuclearAndGasEligibleButNotAligned()
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
    """Retrieve dataland Eligible but not aligned values based on KPI."""
    if kpi == "Revenue":
        data = data_provider.get_taxonomy_eligible_but_not_aligned_revenue_values_by_data(dataset)
    else:
        data = data_provider.get_taxonomy_eligible_but_not_aligned_capex_values_by_data(dataset)

    if data is None:
        logging.error("Retrieved data is None for KPI: %s", kpi)

    return data


def update_attribute(obj: NuclearAndGasEligibleButNotAligned, field_name: str, values: list) -> None:
    """Set an attribute of the Eligible but not aligned by field name."""
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
    data_source = data_sources.get("taxonomy_eligble_but_not_aligned")
    return map_doc_ref_to_qa_doc_ref(data_source)
