import ast
from pathlib import Path
from typing import Any
from unittest import mock

from azure.ai.documentintelligence.models import AnalyzeResult
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice

from dataland_qa_lab.dataland import (
    company_data,
    data_extraction,
    template_extractor,
)
from dataland_qa_lab.prompting_services import prompting_service
from dataland_qa_lab.review import generate_gpt_request


def test_get_correct_values_from_report() -> list:
    exptected_result = ["No", "No", "No", "Yes", "Yes", "Yes"]

    actual_result = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
        prompting_service.PromptingService.create_main_prompt(1),
        prompting_service.PromptingService.create_sub_prompt_template1(),
    )
    assert exptected_result == actual_result


def test_get_taxonomy_alligned_denominator() -> list:
    exptected_result = ["No", "No", "No", "Yes", "Yes", "Yes"]

    actual_result = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
        prompting_service.PromptingService.create_main_prompt(2),
        prompting_service.PromptingService.create_sub_prompt_template2to4(),
    )
    assert exptected_result == actual_result


def test_get_taxonomy_alligned_numerator() -> list:
    exptected_result = ["No", "No", "No", "Yes", "Yes", "Yes"]

    actual_result = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
        prompting_service.PromptingService.create_main_prompt(3),
        prompting_service.PromptingService.create_sub_prompt_template2to4(),
    )
    assert exptected_result == actual_result


def test_get_taxonomy_eligible_not_alligned() -> list:
    exptected_result = ["No", "No", "No", "Yes", "Yes", "Yes"]

    actual_result = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
        prompting_service.PromptingService.create_main_prompt(4),
        prompting_service.PromptingService.create_sub_prompt_template2to4(),
    )
    assert exptected_result == actual_result


def test_get_taxonomy_taxonomy_non_eligible() -> list:
    exptected_result = ["No", "No", "No", "Yes", "Yes", "Yes"]

    actual_result = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
        prompting_service.PromptingService.create_main_prompt(5),
        prompting_service.PromptingService.create_sub_prompt_template2to4(),
    )
    assert exptected_result == actual_result


def create_document_intelligence_mock() -> AnalyzeResult:
    return AnalyzeResult(content="")


def build_simple_openai_chat_completion(message: str) -> ChatCompletion:
    return ChatCompletion(
        id="test",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content=message,
                    role="assistant",
                ),
            )
        ],
        created=0,
        model="test",
        object="chat.completion",
    )


@mock.patch("openai.resources.chat.Completions.create", return_value=build_simple_openai_chat_completion("No"))
@mock.patch(
    "dataland_qa_lab.dataland.data_extraction.extract_text_of_pdf", return_value=create_document_intelligence_mock()
)
def test_extract_page(mock_create: Any, mock_extract_text_of_pdf: Any) -> None:  # noqa: ANN401, ARG001
    project_root = Path(__file__).resolve().parent.parent.parent
    path = project_root / "data" / "pdfs" / "covestro.pdf"
    page_tmp = company_data.CompanyData.get_company_pages()
    page = page_tmp[1]

    actual_result = data_extraction.ectract_page(page[0], path)

    assert actual_result == AnalyzeResult(content="")


def test_extract_template() -> None:
    arguments = """{"1": "No", "2": "No", "3": "No", "4": "No", "5": "Yes", "6": "No"}"""
    te = template_extractor.TemplateExtractor()
    result = te.format_json(arguments)
    # Erwartetes Ergebnis
    expected_result = """row1: ['No']"""

    # Test
    assert result[0] == expected_result


def test_generate_gpt_request(mainprompt: str, subprompt: str) -> list:  # noqa: ARG001
    arguments = """{"1": "No", "2": "No", "3": "No", "4": "Yes", "5": "Yes", "6": "Yes"}"""
    data_dict = ast.literal_eval(arguments)
    assert arguments == data_dict
