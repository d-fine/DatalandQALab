from unittest.mock import Mock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice

from dataland_qa_lab.review.report_generator import yes_no_report_generator
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection
from tests.utils.provide_test_data_collection import provide_test_data_collection
from tests.utils.provide_test_dataset import provide_test_dataset


def create_document_intelligence_mock() -> AnalyzeResult:
    return AnalyzeResult(content="")


def build_simple_openai_chat_completion() -> ChatCompletion:
    msg = "['Yes', 'No', 'Yes', 'Yes', 'Yes', 'No']"
    return ChatCompletion(
        id="test",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content=msg,
                    role="assistant",
                ),
            )
        ],
        created=0,
        model="test",
        object="chat.completion",
    )


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_compare_yes_no_values(mock_generate_gpt_request: Mock) -> None:
    test_data_collection = provide_test_data_collection()
    mock_generate_gpt_request.return_value = [
        "Yes",
        "No",
        "Yes",
        "No",
        "Yes",
        "No",
    ]
    report = yes_no_report_generator.build_yes_no_report(dataset=test_data_collection, relevant_pages=AnalyzeResult())

    assert report.nuclear_energy_related_activities_section426.corrected_data.value is None
    assert report.nuclear_energy_related_activities_section426.comment == "Geprüft durch AzureOpenAI"
    assert report.fossil_gas_related_activities_section430.corrected_data.value == "Yes"


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_build_yes_no_report_success(mock_generate_gpt_request: Mock) -> None:
    mock_generate_gpt_request.return_value = [
        "No",
        "No",
        "Yes",
        "No",
        "No",
        "No",
    ]
    test_data_collection = NuclearAndGasDataCollection(provide_test_dataset())
    report = yes_no_report_generator.build_yes_no_report(dataset=test_data_collection, relevant_pages=AnalyzeResult())

    # Assertions
    assert report.fossil_gas_related_activities_section430.comment == (
        "Discrepancy in 'fossil_gas_related_activities_section430': YesNo.YES != YesNo.NO."
    )
    assert report.fossil_gas_related_activities_section430.verdict == QaReportDataPointVerdict.QAREJECTED


@patch("dataland_qa_lab.review.yes_no_value_generator.get_yes_no_values_from_report")
def test_build_yes_no_report_generator_error(mock_get_yes_no_values: Mock) -> None:
    mock_get_yes_no_values.side_effect = ValueError("Error in get_yes_no_values_from_report")

    test_data_collection = provide_test_data_collection()
    report = yes_no_report_generator.build_yes_no_report(dataset=test_data_collection, relevant_pages="123")

    assert report.nuclear_energy_related_activities_section426.comment == "Error in get_yes_no_values_from_report"
    assert report.nuclear_energy_related_activities_section426.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert report.nuclear_energy_related_activities_section426.corrected_data.value is None


@patch("dataland_qa_lab.dataland.data_provider.get_yes_no_values_by_data")
def test_build_yes_no_report_data_provider_error(mock_get_yes_no_values_by_data: Mock) -> None:
    mock_get_yes_no_values_by_data.side_effect = ValueError("Error in get_yes_no_values_by_data")
    expected_comments = [
        "Error in get_yes_no_values_by_data",
        "Error extracting values from template 1: An unexpected error occurred: "
        "Error during GPT request creation: Connection error.",
    ]
    test_data_collection = provide_test_data_collection()
    report = yes_no_report_generator.build_yes_no_report(dataset=test_data_collection, relevant_pages="123")

    assert report.nuclear_energy_related_activities_section426.comment in expected_comments
    assert report.nuclear_energy_related_activities_section426.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert report.nuclear_energy_related_activities_section426.corrected_data.comment is None
