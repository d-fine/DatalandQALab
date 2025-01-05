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
        nuclearAndGasTaxonomyEligibleButNotAlignedRevenue=build_revenue_eligible_but_not_aligned_frame(dataset, relevant_pages, "Revenue"),
        nuclearAndGasTaxonomyEligibleButNotAlignedCapex=build_revenue_eligible_but_not_aligned_frame(dataset, relevant_pages, "CapEx")
    )


def build_revenue_eligible_but_not_aligned_frame(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult, kpi: str
) -> QaReportDataPointExtendedDataPointNuclearAndGasEligibleButNotAligned:
    """Build report frame for the taxonomy eligible but not alinged data."""
    eligible_but_not_aligned, verdict, comment = compare_eligible_but_not_aligned_values(dataset, relevant_pages, kpi)

    return QaReportDataPointExtendedDataPointNuclearAndGasEligibleButNotAligned(
        comment=comment,
        verdict=verdict,
        correctedData=ExtendedDataPointNuclearAndGasEligibleButNotAligned(
            value=eligible_but_not_aligned,
            quality="Incomplete",
            comment=comment,
            dataSource=get_data_source(dataset),
        ),
    )


def compare_eligible_but_not_aligned_values(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult, kpi: str
) -> tuple[NuclearAndGasEligibleButNotAligned, QaReportDataPointVerdict, str]:
    """Compare taxonomy eligible but not alingned values and return results."""
    eligble_but_not_aligned_values = NumericValueGenerator.get_taxonomy_eligible_not_alligned(relevant_pages, kpi)
    dataland_taxonomy_eligble_but_not_aligned = None
    if (kpi == "Revenue"):
        dataland_taxonomy_eligble_but_not_aligned = (
            data_provider.get_taxonomy_eligible_but_not_aligned_revenue_values_by_data(dataset)
        )
    else:
        dataland_taxonomy_eligble_but_not_aligned = (
            data_provider.get_taxonomy_eligible_but_not_aligned_capex_values_by_data(dataset)
        )
    eligible_but_not_aligned = NuclearAndGasEligibleButNotAligned()
    verdict = QaReportDataPointVerdict.QAACCEPTED
    comment = ""
    current_index = 0

    for field_name, dataland_value_list in dataland_taxonomy_eligble_but_not_aligned.items():
        # Extract the corresponding slice from dominator_values
        prompt_value_list = eligble_but_not_aligned_values[current_index : current_index + 3]
        correct_value_list = dataland_value_list
        if dataland_value_list != prompt_value_list:
            verdict = QaReportDataPointVerdict.QAREJECTED
            discrepancies = ", ".join(
                f"{v1} != {v2}" for v1, v2 in zip(dataland_value_list, prompt_value_list, strict=False) if v1 != v2
            )
            comment += f" Discrepancy in '{field_name}': {discrepancies}."

        setattr(
            eligible_but_not_aligned,
            field_name,
            NuclearAndGasEnvironmentalObjective(
                mitigationAndAdaptation=correct_value_list[0],
                mitigation=correct_value_list[1],
                adaptation=correct_value_list[2],
            ),
        )
        # Update the current index for the next slice
        current_index += 3

    return eligible_but_not_aligned, verdict, comment


def get_data_source(dataset: NuclearAndGasDataCollection) -> ExtendedDocumentReference | None:
    """Retrieve the data source mapped to a QA document reference."""
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_numeric_values(data=dataset)
    data_source = data_sources.get("taxonomy_eligble_but_not_aligned")
    return map_doc_ref_to_qa_doc_ref(data_source)
