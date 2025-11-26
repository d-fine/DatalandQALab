from unittest.mock import MagicMock, Mock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.review.report_generator import non_eligible_report_generator as report_generator
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection
from tests.utils.provide_test_dataset import provide_test_dataset


def provide_test_data_collection() -> tuple[NuclearAndGasDataCollection, AnalyzeResult]:
    dataset = provide_test_dataset()
    data_collection = NuclearAndGasDataCollection(dataset)
    relevant_pages = MagicMock(spec=AnalyzeResult)
    return data_collection, relevant_pages


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_taxonomy_non_eligible_report(mock_generate_gpt_request: Mock) -> None:
    """Tests the generation of taxonomy-aligned numerator report."""
    dataset, relevant_pages = provide_test_data_collection()
    mock_generate_gpt_request.return_value = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        0.65,
    ]
    report = report_generator.build_taxonomy_non_eligible_report(dataset, relevant_pages)

    assert report is not None
    assert report.nuclear_and_gas_taxonomy_non_eligible_revenue is not None
    assert report.nuclear_and_gas_taxonomy_non_eligible_revenue.corrected_data is not None
    assert report.nuclear_and_gas_taxonomy_non_eligible_revenue.corrected_data.value is None


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_revenue_taxonomy_non_eligible_report_frame(mock_generate_gpt_request: Mock) -> None:
    """Tests the generation of revenue numerator report frame."""
    dataset, relevant_pages = provide_test_data_collection()
    mock_generate_gpt_request.return_value = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        0.65,
    ]
    report_frame = report_generator.build_non_eligible_report_frame(dataset, relevant_pages, "Revenue")

    assert report_frame is not None
    assert "Error retrieving prompted values for template 5" in report_frame.comment
    assert report_frame.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert report_frame.corrected_data.value is None


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_compare_taxonomy_non_eligible_values(mock_generate_gpt_request: Mock) -> None:
    """Tests the comparison of taxonomy numerator values."""
    dataset, relevant_pages = provide_test_data_collection()
    mock_generate_gpt_request.return_value = [
        None,
        None,
        None,
        None,
        None,
        None,
        1,
        0.7,
    ]
    report_frame = report_generator.build_non_eligible_report_frame(dataset, relevant_pages, "Revenue")

    assert report_frame.corrected_data is not None
    assert report_frame.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert "Error retrieving prompted values for template 5" in report_frame.comment


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_compare_taxonomy_non_eligible_values_edge_cases(mock_generate_gpt_request: Mock) -> None:
    dataset, relevant_pages = provide_test_data_collection()
    mock_generate_gpt_request.return_value = [-1.0] * 8

    report = report_generator.build_non_eligible_report_frame(dataset, relevant_pages, "Revenue")

    assert report is not None
    assert report.verdict == QaReportDataPointVerdict.QAREJECTED
    assert report.corrected_data.quality == "Reported"


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
@patch("dataland_qa_lab.dataland.data_provider.get_taxonomy_non_eligible_revenue_values_by_data")
def test_generate_revenue_denominator_report_frame_not_attempted(
    mock_get_dataland_values: Mock, mock_generate_gpt_request: Mock
) -> None:
    dataset, relevant_pages = provide_test_data_collection()

    # Simulate an exception in dataland value retrieval
    mock_generate_gpt_request.side_effect = ValueError("Mock GPT error")
    report = report_generator.build_non_eligible_report_frame(dataset, relevant_pages, "Revenue")

    assert report is not None
    assert report.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert "Error retrieving prompted values for template 5" in report.comment

    # Simulate an exception in dataland retrieval
    mock_generate_gpt_request.side_effect = None
    mock_get_dataland_values.side_effect = RuntimeError("Mock dataland error")
    report = report_generator.build_non_eligible_report_frame(dataset, relevant_pages, "Revenue")

    assert report is not None
    assert report.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert "Error retrieving dataland values for template 5" in report.comment


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_taxonomy_aligned_denominator_report_edge_cases_not_attempted(mock_generate_gpt_request: Mock) -> None:
    dataset, relevant_pages = provide_test_data_collection()

    # Simulate an exception in the GPT request generation
    mock_generate_gpt_request.side_effect = ValueError("Mock GPT error")

    report = report_generator.build_non_eligible_report_frame(dataset, relevant_pages, "Revenue")

    assert report is not None
    assert report.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert "Error retrieving prompted values for template 5" in report.comment
