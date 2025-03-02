from unittest.mock import MagicMock, Mock, patch

from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

import dataland_qa_lab.review.report_generator.denominator_report_generator as report_generator
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection
from tests.utils.provide_test_dataset import provide_test_dataset


def provide_test_data_collection() -> tuple[NuclearAndGasDataCollection, str]:
    dataset = provide_test_dataset()
    data_collection = NuclearAndGasDataCollection(dataset)
    relevant_pages = MagicMock(spec=str)
    return data_collection, relevant_pages


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_taxonomy_aligned_denominator_report(mock_generate_gpt_request: Mock) -> None:
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
    assert report.nuclear_and_gas_taxonomy_aligned_revenue_denominator.corrected_data.value is None


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_revenue_denominator_report_frame(mock_generate_gpt_request: Mock) -> None:
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
    assert report_frame.corrected_data.value is None


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_compare_taxonomy_denominator_values(mock_generate_gpt_request: Mock) -> None:
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
        0.04,
        0.03,
        0.0,
        0.04,
        0.03,
        0.1,
    ]
    revenue_report = report_generator.build_denominator_report_frame(dataset, relevant_pages, "Revenue")

    assert (
        revenue_report.corrected_data.value.taxonomy_aligned_share_denominator_n_and_g426.mitigation_and_adaptation
        is None
    )
    assert revenue_report.corrected_data.value.taxonomy_aligned_share_denominator_n_and_g426.mitigation is None
    assert revenue_report.corrected_data.value.taxonomy_aligned_share_denominator_n_and_g426.adaptation is None

    assert (
        revenue_report.corrected_data.value.taxonomy_aligned_share_denominator_n_and_g430.mitigation_and_adaptation
        == 0.0
    )
    assert revenue_report.corrected_data.value.taxonomy_aligned_share_denominator_n_and_g430.mitigation == 0.0
    assert revenue_report.corrected_data.value.taxonomy_aligned_share_denominator_n_and_g430.adaptation == 0.0

    assert revenue_report.verdict == QaReportDataPointVerdict.QAREJECTED
    assert revenue_report.comment == "Discrepancy in 'taxonomy_aligned_share_denominator': 0.0 != 0.1."


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_taxonomy_aligned_denominator_report_edge_cases(mock_generate_gpt_request: Mock) -> None:
    dataset, relevant_pages = provide_test_data_collection()
    mock_generate_gpt_request.return_value = [-1.0] * 24

    report = report_generator.build_denominator_report_frame(dataset, relevant_pages, "Revenue")

    assert report is not None
    assert report.verdict == QaReportDataPointVerdict.QAREJECTED
    assert report.corrected_data.quality == "NoDataFound"


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
@patch("dataland_qa_lab.dataland.data_provider.get_taxonomy_aligned_revenue_denominator_values_by_data")
def test_generate_revenue_denominator_report_frame_not_attempted(
    mock_get_dataland_values: Mock, mock_generate_gpt_request: Mock
) -> None:
    dataset, relevant_pages = provide_test_data_collection()

    mock_generate_gpt_request.side_effect = ValueError("Mock GPT error")
    report = report_generator.build_denominator_report_frame(dataset, relevant_pages, "Revenue")

    assert report is not None
    assert report.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert "Error retrieving prompted values for template 2" in report.comment

    mock_generate_gpt_request.side_effect = None
    mock_get_dataland_values.side_effect = RuntimeError("Mock dataland error")
    report = report_generator.build_denominator_report_frame(dataset, relevant_pages, "Revenue")

    assert report is not None
    assert report.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert "Error retrieving dataland values for template 2" in report.comment


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_taxonomy_aligned_denominator_report_edge_cases_not_attempted(mock_generate_gpt_request: Mock) -> None:
    dataset, relevant_pages = provide_test_data_collection()

    mock_generate_gpt_request.side_effect = ValueError("Mock GPT error")

    report = report_generator.build_denominator_report_frame(dataset, relevant_pages, "Revenue")

    assert report is not None
    assert report.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert "Error retrieving prompted values for template 2" in report.comment
