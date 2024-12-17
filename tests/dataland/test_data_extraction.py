from unittest.mock import Mock, patch

import pytest

from dataland_qa_lab.prompting_services import prompting_service
from dataland_qa_lab.review import generate_gpt_request


@pytest.fixture
def mock_openai_response() -> list:
    """Erstellt eine simulierte GPT-Antwort mit tool_calls."""
    class MockToolCall:
        arguments = "{'1': 'Yes', '2': 'No', '3': 'Yes', '4': 'No', '5': 'Yes', '6': 'No'}"

    class MockMessage:
        tool_calls = [MockToolCall()]  # noqa: RUF012

    class MockChoice:
        message = MockMessage()

    class MockResponse:
        choices = [MockChoice()]  # noqa: RUF012

    return MockResponse()


@pytest.fixture
def mock_pdf() -> Mock:
    pdf = Mock()
    pdf.content = "This is a test PDF content."
    return pdf


@patch("openai.AzureOpenAI")
def test_generate_gpt_request(mock_azure_openai: Mock, mock_openai_response: list, mock_pdf: Mock) -> None:

    mock_client_instance = Mock()
    mock_client_instance.chat.completions.create.return_value = mock_openai_response
    mock_azure_openai.return_value = mock_client_instance

    mainprompt = prompting_service.PromptingService.create_main_prompt(1, mock_pdf)
    subprompt = prompting_service.PromptingService.create_sub_prompt_template1()

    result = generate_gpt_request.GenerateGptRequest.generate_gpt_request(mainprompt, subprompt)

    expected_result = ['No', 'No', 'No', 'No', 'No', 'No']  # noqa: Q000
    assert result == expected_result, "Die Rückgabewerte stimmen nicht überein."
