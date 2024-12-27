from unittest.mock import Mock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

import dataland_qa_lab.review.report_generator.denominator_report_generator as report_generator
from dataland_qa_lab.dataland.dataset_provider import get_dataset_by_id
from dataland_qa_lab.pages.pages_provider import get_relevant_pages_of_pdf
from dataland_qa_lab.pages.text_to_doc_intelligence import extract_text_of_pdf
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def provide_test_data() -> tuple[NuclearAndGasDataCollection, AnalyzeResult]:
    """Provides mock data for testing purposes."""
    dataset_id = "fae59f2e-c438-4457-9a74-55c0db006fee"
    dataset = get_dataset_by_id(dataset_id).data
    data_collection = NuclearAndGasDataCollection(dataset)

    relevant_pages = get_relevant_pages_of_pdf(data_collection)
    return data_collection, extract_text_of_pdf(relevant_pages)


@patch("dataland_qa_lab.review.numeric_value_generator.NumericValueGenerator.get_taxonomy_alligned_denominator")
def test_generate_taxonomy_aligned_denominator_report(mock_get_taxonomy_aligned_denominator: Mock) -> None:
    """Tests the generation of taxonomy-aligned denominator report."""
    dataset, relevant_pages = provide_test_data()

    # Mock the denominator values
    mock_get_taxonomy_aligned_denominator.return_value = [
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
        0.0,
    ]

    # Call the function under test
    report = report_generator.build_taxonomy_aligned_denominator_report(dataset, relevant_pages)

    # Perform assertions
    assert report is not None
    assert report.nuclear_and_gas_taxonomy_aligned_revenue_denominator is not None
    assert report.nuclear_and_gas_taxonomy_aligned_revenue_denominator.corrected_data is not None
    assert report.nuclear_and_gas_taxonomy_aligned_revenue_denominator.corrected_data.value is not None


@patch("dataland_qa_lab.review.numeric_value_generator.NumericValueGenerator.get_taxonomy_alligned_denominator")
def test_generate_revenue_denominator_report_frame(mock_get_taxonomy_aligned_denominator: Mock) -> None:
    """Tests the generation of revenue denominator report frame."""
    dataset, relevant_pages = provide_test_data()

    # Mock the denominator values
    mock_get_taxonomy_aligned_denominator.return_value = [
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
        0.0,
    ]

    # Call the function under test
    report_frame = report_generator.build_revenue_denominator_report_frame(dataset, relevant_pages)

    # Perform assertions
    assert report_frame is not None
    assert not report_frame.comment
    assert report_frame.verdict == QaReportDataPointVerdict.QAACCEPTED
    assert report_frame.corrected_data is not None


@patch("dataland_qa_lab.review.numeric_value_generator.NumericValueGenerator.get_taxonomy_alligned_denominator")
def test_compare_taxonomy_denominator_values(mock_get_taxonomy_aligned_denominator: Mock) -> None:
    """Tests the comparison of taxonomy denominator values."""
    dataset, relevant_pages = provide_test_data()

    # Mock the denominator values
    mock_get_taxonomy_aligned_denominator.return_value = [
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

    # Call the function under test
    aligned_denominator, verdict, comment = report_generator.compare_denominator_values(dataset, relevant_pages)

    # Perform assertions
    assert aligned_denominator is not None
    assert verdict == QaReportDataPointVerdict.QAREJECTED
    assert comment == " Discrepancy in 'taxonomy_aligned_share_denominator': 0.0 != 0.1."
