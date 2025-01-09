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
    """Build report frame for the taxonomy eligible but not alinged data."""
    eligible_but_not_aligned, verdict, comment = compare_eligible_but_not_aligned_values(dataset, relevant_pages, kpi)

    corrected_data = (
        ExtendedDataPointNuclearAndGasEligibleButNotAligned(
            value=eligible_but_not_aligned,
            quality="Incomplete",
            comment=comment,
            dataSource=get_data_source(dataset),
        )
        if verdict != QaReportDataPointVerdict.QAACCEPTED
        else ExtendedDataPointNuclearAndGasEligibleButNotAligned()
    )

    return QaReportDataPointExtendedDataPointNuclearAndGasEligibleButNotAligned(
        comment=comment, verdict=verdict, correctedData=corrected_data
    )


def compare_eligible_but_not_aligned_values(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult, kpi: str
) -> tuple[NuclearAndGasEligibleButNotAligned, QaReportDataPointVerdict, str]:
    """Compare Eligible but not aligned values and return results."""
    # Generate prompted values and split them into chunks
    prompted_values = NumericValueGenerator.get_taxonomy_eligible_not_alligned(relevant_pages, kpi)
    chunked_prompted_values = [prompted_values[i : i + 3] for i in range(0, len(prompted_values), 3)]

    dataland_values = get_dataland_values(dataset, kpi)

    eligible_but_not_aligned = None
    verdict = QaReportDataPointVerdict.QAACCEPTED
    comments = []

    for (field_name, dataland_vals), prompt_vals in zip(dataland_values.items(), chunked_prompted_values, strict=False):
        if dataland_vals != prompt_vals:
            verdict = QaReportDataPointVerdict.QAREJECTED
            discrepancies = generate_discrepancies(dataland_vals, prompt_vals)
            comments.append(f"Discrepancy in '{field_name}': {discrepancies}.")
            eligible_but_not_aligned = (
                NuclearAndGasEligibleButNotAligned() if eligible_but_not_aligned is None else eligible_but_not_aligned
            )
            update_attribute(eligible_but_not_aligned, field_name, prompt_vals)

    return eligible_but_not_aligned, verdict, "".join(comments)


def get_dataland_values(dataset: NuclearAndGasDataCollection, kpi: str) -> dict:
    """Retrieve dataland Eligible but not aligned values based on KPI."""
    if kpi == "Revenue":
        return data_provider.get_taxonomy_eligible_but_not_aligned_revenue_values_by_data(dataset)
    return data_provider.get_taxonomy_eligible_but_not_aligned_capex_values_by_data(dataset)


def generate_discrepancies(dataland_values: list, prompted_values: list) -> str:
    """Generate a string describing discrepancies between two lists of values."""
    return ", ".join(f"{v1} != {v2}" for v1, v2 in zip(dataland_values, prompted_values, strict=False) if v1 != v2)


def update_attribute(obj: NuclearAndGasEligibleButNotAligned, field_name: str, values: list) -> None:
    """Set an attribute of the Eligible but not aligned by field name."""
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
