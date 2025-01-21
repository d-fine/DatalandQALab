from unittest.mock import MagicMock, Mock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.review.report_generator import eligible_not_aligned_report_generator as report_generator
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection
from tests.utils.provide_test_dataset import provide_test_dataset


def provide_test_data_collection() -> tuple[NuclearAndGasDataCollection, AnalyzeResult]:
    dataset = provide_test_dataset()
    data_collection = NuclearAndGasDataCollection(dataset)
    relevant_pages = MagicMock(spec=AnalyzeResult)
    return data_collection, relevant_pages


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_build_taxonomy_eligible_but_not_aligned_report(mock_generate_gpt_request: Mock) -> None:
    """Tests the generation of taxonomy Eligible but not aligned report."""
    dataset, relevant_pages = provide_test_data_collection()
    mock_generate_gpt_request.return_value = [
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.26,
        0.2,
        0.0,
        0.26,
        0.2,
        0.0,
    ]
    report = report_generator.build_taxonomy_eligible_but_not_aligned_report(dataset, relevant_pages)

    assert report is not None
    assert report.nuclear_and_gas_taxonomy_eligible_but_not_aligned_revenue is not None
    assert report.nuclear_and_gas_taxonomy_eligible_but_not_aligned_revenue.corrected_data.value is None


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_revenue_denominator_report_frame(mock_generate_gpt_request: Mock) -> None:
    """Tests the generation of revenue Eligible but not aligned report frame."""
    dataset, relevant_pages = provide_test_data_collection()
    mock_generate_gpt_request.return_value = [
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.26,
        0.2,
        0.0,
        0.26,
        0.2,
        0.0,
    ]
    report_frame = report_generator.build_eligible_but_not_aligned_frame(dataset, relevant_pages, "Revenue")

    assert report_frame is not None
    assert not report_frame.comment
    assert report_frame.verdict == QaReportDataPointVerdict.QAACCEPTED
    assert report_frame.corrected_data.value is None


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_compare_taxonomy_denominator_values(mock_generate_gpt_request: Mock) -> None:
    """Tests the comparison of taxonomy Eligible but not aligned values."""
    dataset, relevant_pages = provide_test_data_collection()
    mock_generate_gpt_request.return_value = [
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.26,
        0.2,
        0.0,
        0.26,
        0.3,
        0.1,
    ]
    revenue_report = report_generator.build_eligible_but_not_aligned_frame(dataset, relevant_pages, "Revenue")

    assert (
        revenue_report.corrected_data.value.taxonomy_eligible_but_not_aligned_share_n_and_g426.mitigation_and_adaptation
        is None
    )
    assert revenue_report.corrected_data.value.taxonomy_eligible_but_not_aligned_share_n_and_g426.mitigation is None
    assert revenue_report.corrected_data.value.taxonomy_eligible_but_not_aligned_share_n_and_g426.adaptation is None
    # assert 0.0 values
    assert (
        revenue_report.corrected_data.value.taxonomy_eligible_but_not_aligned_share_n_and_g430.mitigation_and_adaptation
        == 0.0
    )
    assert revenue_report.corrected_data.value.taxonomy_eligible_but_not_aligned_share_n_and_g430.mitigation == 0.0
    assert revenue_report.corrected_data.value.taxonomy_eligible_but_not_aligned_share_n_and_g430.adaptation == 0.0

    assert revenue_report.verdict == QaReportDataPointVerdict.QAREJECTED
    assert revenue_report.comment == (
        "Discrepancy in 'taxonomy_eligible_but_not_aligned_share': 0.2 != 0.3."
        "Discrepancy in 'taxonomy_eligible_but_not_aligned_share': 0.0 != 0.1."
    )


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_eligible_but_not_aligned_report_edge_cases(mock_generate_gpt_request: Mock) -> None:
    dataset, relevant_pages = provide_test_data_collection()
    mock_generate_gpt_request.return_value = [-1.0] * 24

    report = report_generator.build_eligible_but_not_aligned_frame(dataset, relevant_pages, "Revenue")

    assert report is not None
    assert report.verdict == QaReportDataPointVerdict.QAREJECTED
    assert report.corrected_data.quality == "NoDataFound"
