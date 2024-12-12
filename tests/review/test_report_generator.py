from unittest.mock import Mock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice

from dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator import NuclearAndGasReportGenerator
from tests.utils.provide_test_data_collection import provide_test_data_collection


def test_build_report_frame() -> None:
    report_frame = NuclearAndGasReportGenerator().build_report_frame()

    assert report_frame is not None
    assert report_frame.general.taxonomy_aligned_denominator is not None


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


@patch("openai.resources.chat.Completions.create", return_value=build_simple_openai_chat_completion())
def test_compare_yes_no_values(_mock_create: Mock) -> None:  # noqa: PT019
    test_data_collection = provide_test_data_collection()

    corrected_values = NuclearAndGasReportGenerator().compare_yes_no_values(
        dataset=test_data_collection, relevant_pages=AnalyzeResult()
    )

    assert corrected_values.get("nuclear_energy_related_activities_section426").corrected_data.value is None
    assert corrected_values.get("nuclear_energy_related_activities_section426").comment == "Geprüft durch AzureOpenAI"
    assert corrected_values.get("fossil_gas_related_activities_section430").corrected_data.value == "Yes"


@patch("openai.resources.chat.Completions.create", return_value=build_simple_openai_chat_completion())
def test_generate_report(_mock_create: Mock) -> None:  # noqa: PT019
    test_data_collection = provide_test_data_collection()

    report = NuclearAndGasReportGenerator().generate_report(
        relevant_pages=AnalyzeResult(), dataset=test_data_collection
    )

    assert report is not None
    assert report.general.general.fossil_gas_related_activities_section430.corrected_data.value == "Yes"
