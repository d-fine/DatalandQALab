from unittest.mock import Mock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.dataland.dataset_provider import get_dataset_by_id
from dataland_qa_lab.pages.pages_provider import get_relevant_pages_of_pdf
from dataland_qa_lab.pages.text_to_doc_intelligence import extract_text_of_pdf
from dataland_qa_lab.review.report_generator import eligible_not_aligned_report_generator
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def provide_test_data() -> tuple[NuclearAndGasDataCollection, AnalyzeResult]:
    dataset_id = "fae59f2e-c438-4457-9a74-55c0db006fee"
    dataset = get_dataset_by_id(dataset_id).data
    data_collection = NuclearAndGasDataCollection(dataset)

    relevant_pages = get_relevant_pages_of_pdf(data_collection)
    return data_collection, extract_text_of_pdf(relevant_pages)


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_build_taxonomy_eligible_but_not_aligned_report(mock_generate_gpt_request: Mock) -> None:
    """Tests the generation of taxonomy-aligned numerator report."""
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
        0.26,
        0.2,
        0.0,
        0.26,
        0.2,
        0.0,
    ]
    report = eligible_not_aligned_report_generator.build_taxonomy_eligible_but_not_aligned_report(
        dataset, relevant_pages
    )

    assert report is not None
    assert report.nuclear_and_gas_taxonomy_eligible_but_not_aligned_revenue is not None
    assert report.nuclear_and_gas_taxonomy_eligible_but_not_aligned_revenue.corrected_data is not None
    assert report.nuclear_and_gas_taxonomy_eligible_but_not_aligned_revenue.corrected_data.value is not None


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_revenue_denominator_report_frame(mock_generate_gpt_request: Mock) -> None:
    """Tests the generation of revenue numerator report frame."""
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
        0.26,
        0.2,
        0.0,
        0.26,
        0.2,
        0.0,
    ]
    report_frame = eligible_not_aligned_report_generator.build_revenue_eligible_but_not_aligned_frame(
        dataset, relevant_pages
    )

    assert report_frame is not None
    assert not report_frame.comment
    assert report_frame.verdict == QaReportDataPointVerdict.QAACCEPTED
    assert report_frame.corrected_data is not None


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_compare_taxonomy_denominator_values(mock_generate_gpt_request: Mock) -> None:
    """Tests the comparison of taxonomy numerator values."""
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
        0.26,
        0.2,
        0.0,
        0.26,
        0.3,
        0.1,
    ]
    aligned_denominator, verdict, comment = (
        eligible_not_aligned_report_generator.compare_eligible_but_not_aligned_values(dataset, relevant_pages)
    )

    assert aligned_denominator is not None
    assert verdict == QaReportDataPointVerdict.QAREJECTED
    assert comment == (" Discrepancy in 'taxonomy_eligible_but_not_aligned_share': 0.2 != 0.3, 0.0 != 0.1.")
