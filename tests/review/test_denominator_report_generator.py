from unittest.mock import MagicMock, Mock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

import dataland_qa_lab.review.report_generator.denominator_report_generator as report_generator
from dataland_qa_lab.dataland.dataset_provider import get_dataset_by_id
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def provide_test_data() -> tuple[NuclearAndGasDataCollection, AnalyzeResult]:
    dataset_id = "7b7c7ea2-7d74-4161-afc8-4aa6bcde66c7"
    dataset = get_dataset_by_id(dataset_id).data
    data_collection = NuclearAndGasDataCollection(dataset)

    relevant_pages = MagicMock(spec=AnalyzeResult)

    return data_collection, relevant_pages


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_taxonomy_aligned_denominator_report(mock_generate_gpt_request: Mock) -> None:
    """Tests the generation of taxonomy-aligned denominator report."""
    dataset, relevant_pages = provide_test_data()
    mock_generate_gpt_request.return_value = [
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
    report = report_generator.build_taxonomy_aligned_denominator_report(dataset, relevant_pages)

    assert report is not None
    assert report.nuclear_and_gas_taxonomy_aligned_revenue_denominator is not None
    assert report.nuclear_and_gas_taxonomy_aligned_revenue_denominator.corrected_data is not None
    assert report.nuclear_and_gas_taxonomy_aligned_revenue_denominator.corrected_data.value is not None


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_revenue_denominator_report_frame(mock_generate_gpt_request: Mock) -> None:
    """Tests the generation of revenue denominator report frame."""
    dataset, relevant_pages = provide_test_data()
    mock_generate_gpt_request.return_value = [
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
    report_frame = report_generator.build_denominator_report_frame(dataset, relevant_pages, "Revenue")

    assert report_frame is not None
    assert not report_frame.comment
    assert report_frame.verdict == QaReportDataPointVerdict.QAACCEPTED
    assert report_frame.corrected_data is not None


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_compare_taxonomy_denominator_values(mock_generate_gpt_request: Mock) -> None:
    """Tests the comparison of taxonomy denominator values."""
    dataset, relevant_pages = provide_test_data()
    mock_generate_gpt_request.return_value = [
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
    aligned_denominator, verdict, comment = report_generator.compare_denominator_values(
        dataset, relevant_pages, "Revenue"
    )

    assert aligned_denominator is not None
    assert verdict == QaReportDataPointVerdict.QAREJECTED
    assert comment == " Discrepancy in 'taxonomy_aligned_share_denominator': 0.0 != 0.1."
