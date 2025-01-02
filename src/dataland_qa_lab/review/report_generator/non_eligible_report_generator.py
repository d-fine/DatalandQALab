from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.extended_data_point_nuclear_and_gas_non_eligible import (
    ExtendedDataPointNuclearAndGasNonEligible,
)
from dataland_qa.models.extended_document_reference import ExtendedDocumentReference
from dataland_qa.models.nuclear_and_gas_general_taxonomy_non_eligible import NuclearAndGasGeneralTaxonomyNonEligible
from dataland_qa.models.nuclear_and_gas_non_eligible import NuclearAndGasNonEligible
from dataland_qa.models.qa_report_data_point_extended_data_point_nuclear_and_gas_non_eligible import (
    QaReportDataPointExtendedDataPointNuclearAndGasNonEligible,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review.numeric_value_generator import NumericValueGenerator
from dataland_qa_lab.utils.doc_ref_to_qa_ref_mapper import map_doc_ref_to_qa_doc_ref
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def build_taxonomy_non_eligible_report(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult
) -> NuclearAndGasGeneralTaxonomyNonEligible:
    """Create Report Frame for the Nuclear and Gas General Taxonomy Non Eligible."""
    return NuclearAndGasGeneralTaxonomyNonEligible(
        nuclear_and_gas_taxonomy_non_eligible_revenue=build_revenue_non_eligible_report_frame(dataset, relevant_pages)
    )


def build_revenue_non_eligible_report_frame(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult
) -> QaReportDataPointExtendedDataPointNuclearAndGasNonEligible:
    """Build report frame for the revenue non_eligible."""
    non_eligible, verdict, comment = compare_non_eligible_values(dataset, relevant_pages)

    return QaReportDataPointExtendedDataPointNuclearAndGasNonEligible(
        comment=comment,
        verdict=verdict,
        correctedData=ExtendedDataPointNuclearAndGasNonEligible(
            value=non_eligible,
            quality="Incomplete",
            comment=comment,
            dataSource=get_data_source(dataset),
        ),
    )


def compare_non_eligible_values(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult
) -> tuple[NuclearAndGasNonEligible, QaReportDataPointVerdict, str]:
    """Compare non_eligible_values values and return results."""
    promt_non_eligible_values = NumericValueGenerator.get_taxonomy_non_eligible(relevant_pages)
    dataland_non_eligible_values = data_provider.get_taxonomy_non_eligible_revenue_values_by_data(dataset)

    value = NuclearAndGasNonEligible()
    verdict = QaReportDataPointVerdict.QAACCEPTED
    comment = ""

    for index, (field_name, dataland_value) in enumerate(dataland_non_eligible_values.items()):
        try:
            prompt_value = promt_non_eligible_values[index]
        except IndexError:
            verdict = QaReportDataPointVerdict.QAREJECTED
            comment += f" Missing value for '{field_name}' in non_eligible_values."
            continue
        correct_value = dataland_value
        if dataland_value != prompt_value:
            verdict = QaReportDataPointVerdict.QAREJECTED
            comment += f" Discrepancy in '{field_name}': {dataland_value} != {prompt_value}."
            correct_value = prompt_value

        setattr(
            value,
            field_name,
            correct_value,
        )

    return value, verdict, comment


def get_data_source(dataset: NuclearAndGasDataCollection) -> ExtendedDocumentReference | None:
    """Retrieve the data source mapped to a QA document reference."""
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_numeric_values(data=dataset)
    data_source = data_sources.get("taxonomy_non_eligible")
    return map_doc_ref_to_qa_doc_ref(data_source)
