from unittest.mock import Mock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

import dataland_qa_lab.review.report_generator.denominator_report_generator as report_genaerator
from dataland_qa_lab.dataland.dataset_provider import get_dataset_by_id
from dataland_qa_lab.pages.pages_provider import get_relevant_pages_of_pdf
from dataland_qa_lab.pages.text_to_doc_intelligence import extract_text_of_pdf
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def provide_test_data() -> tuple[NuclearAndGasDataCollection, AnalyzeResult]:
    dataset_id = "fae59f2e-c438-4457-9a74-55c0db006fee"
    dataset = get_dataset_by_id(dataset_id).data
    data_collection = NuclearAndGasDataCollection(dataset)

    relevant_pages = get_relevant_pages_of_pdf(data_collection)
    return data_collection, extract_text_of_pdf(relevant_pages)


dataset, relevant_pages = provide_test_data()

# for testing purposes
"""dominator_values = NumericValueGenerator.get_taxonomy_alligned_denominator(relevant_pages)
dataland_dominator_values = data_provider.get_taxonomy_aligned_revenue_denominator_values_by_data(dataset)

print(dataland_dominator_values)
print(dominator_values)"""


@patch("dataland_qa_lab.review.numeric_value_generator.NumericValueGenerator.get_taxonomy_alligned_denominator")
def test_build_taxonomy_aligned_denominator_report_frame(mock_get_taxonomy_alligned_denominator: Mock) -> None:
    # Provide test data
    dataset, relevant_pages = provide_test_data()

    mock_get_taxonomy_alligned_denominator.return_value = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.04,
        0.03,
        0.0,
        0.04,
        0.03,
        0.0,
        0.04,
        0.03,
        0.0,
        0.04,
        0.03,
        0.0,
        0.04,
        0.03,
        0.0,
    ]

    # Call the function under test
    denominator_report = report_genaerator.build_taxonomy_aligned_denominator_report(dataset, relevant_pages)

    # Perform assertions
    assert denominator_report is not None
    assert denominator_report.nuclear_and_gas_taxonomy_aligned_revenue_denominator is not None
    assert denominator_report.nuclear_and_gas_taxonomy_aligned_revenue_denominator.corrected_data is not None
    assert denominator_report.nuclear_and_gas_taxonomy_aligned_revenue_denominator.corrected_data.value is not None


@patch("dataland_qa_lab.review.numeric_value_generator.NumericValueGenerator.get_taxonomy_alligned_denominator")
def test_compare_denominator_values(mock_get_taxonomy_alligned_denominator: Mock) -> None:
    # Provide test data
    dataset, relevant_pages = provide_test_data()
    mock_get_taxonomy_alligned_denominator.return_value = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.04,
        0.03,
        0.0,
        0.04,
        0.03,
        0.1,
    ]

    aligned_denominator, verdict, comment = report_genaerator.compare_denominator_values(dataset, relevant_pages)
    assert aligned_denominator is not None
    assert verdict == QaReportDataPointVerdict.QAREJECTED
    assert comment == " Discrepancy in 'taxonomy_aligned_share_denominator': 0.0 != 0.1."
