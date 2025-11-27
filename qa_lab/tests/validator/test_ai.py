from unittest.mock import MagicMock, patch

from qa_lab.validator.ai import execute_prompt

dummy_prompt = "What is 2 + 2?"


@patch("qa_lab.validator.ai.client")
def test_execute_prompt_success(mock_client: MagicMock) -> None:
    """Test that execute_prompt returns correct parsed response."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"answer": 4, "confidence": 1.0, "reasoning": "Basic math"}'))
    ]
    mock_client.chat.completions.create.return_value = mock_response

    result = execute_prompt(dummy_prompt, ai_model="gpt-test", retries=1)
    assert result == {"answer": 4, "confidence": 1.0, "reasoning": "Basic math"}


@patch("qa_lab.validator.ai.client")
def test_execute_prompt_empty_content(mock_client: MagicMock) -> None:
    """Test that empty content response is handled correctly."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=""))]
    mock_client.chat.completions.create.return_value = mock_response

    result = execute_prompt(dummy_prompt, retries=0)
    assert result == {"answer": None, "confidence": 0.0, "reasoning": "No content returned from AI model."}


@patch("qa_lab.validator.ai.client")
def test_execute_prompt_invalid_json(mock_client: MagicMock) -> None:
    """Test that invalid JSON response is handled correctly."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="INVALID JSON"))]
    mock_client.chat.completions.create.return_value = mock_response

    result = execute_prompt(dummy_prompt, retries=0)
    assert result == {"answer": None, "confidence": 0.0, "reasoning": "Couldn't parse response."}


@patch("qa_lab.validator.ai.client")
def test_execute_prompt_retries(mock_client: MagicMock) -> None:
    """Test that retries work correctly on invalid JSON responses."""
    first_response = MagicMock()
    first_response.choices = [MagicMock(message=MagicMock(content="INVALID"))]

    second_response = MagicMock()
    second_response.choices = [
        MagicMock(message=MagicMock(content='{"answer": 42, "confidence": 0.9, "reasoning": "Test"}'))
    ]

    mock_client.chat.completions.create.side_effect = [first_response, second_response]

    result = execute_prompt(dummy_prompt, retries=2)
    assert result == {"answer": 42, "confidence": 0.9, "reasoning": "Test"}
    assert mock_client.chat.completions.create.call_count == 2
