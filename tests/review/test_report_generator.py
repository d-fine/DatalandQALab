from unittest.mock import Mock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice

from dataland_qa_lab.review.report_generator import yes_no_report_generator
from tests.utils.provide_test_data_collection import provide_test_data_collection


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
    assert report.nuclear_energy_related_activities_section426.comment == "Reviewed by AzureOpenAI"
    assert report.fossil_gas_related_activities_section430.corrected_data.value == "Yes"
