import json
from unittest.mock import MagicMock, patch

from dataland_qa_lab.data_point_flow.ai import execute_prompt


@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_execute_prompt_valid_json(mock_client: MagicMock) -> None:
    """Test that execute_prompt returns correct data on valid JSON response."""
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {"predicted_answer": "OK", "confidence": 0.9, "reasoning": "All good", "qa_status": "ACCEPTED"}
                    )
                )
            )
        ]
    )

    result = await execute_prompt("test?", previous_answer="test?", ai_model="gpt-4o")

    assert result.predicted_answer == "OK"
    assert result.confidence == 0.9
    assert result.reasoning == "All good"


@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_execute_prompt_retry_on_invalid_json(mock_client: MagicMock) -> None:
    """Test that execute_prompt retries on invalid JSON responses."""
    mock_client.chat.completions.create.side_effect = [
        MagicMock(choices=[MagicMock(message=MagicMock(content="not json"))]),
        MagicMock(choices=[MagicMock(message=MagicMock(content="still bad"))]),
        MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content=json.dumps(
                            {
                                "predicted_answer": 42,
                                "confidence": 0.8,
                                "reasoning": "Finally valid",
                                "qa_status": "ACCEPTED",
                            }
                        )
                    )
                )
            ]
        ),
    ]

    result = await execute_prompt("test?", previous_answer="test?", ai_model="gpt-4o", retries=3)

    assert result.predicted_answer == 42
    assert result.confidence == 0.8
    assert "Finally valid" in result.reasoning


@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_execute_prompt_no_content(mock_client: MagicMock) -> None:
    """Test that execute_prompt handles no content response with fallback."""
    mock_client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content=None))])

    result = await execute_prompt("test?", previous_answer="test?", ai_model="gpt-4o", retries=1)

    assert result.predicted_answer is None
    assert result.confidence == 0.0
    assert "No content" in result.reasoning


@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_execute_prompt_invalid_json_fallback(mock_client: MagicMock) -> None:
    """Test that execute_prompt falls back after retries on invalid JSON."""
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="invalid"))]
    )

    result = await execute_prompt("test?", previous_answer="test?", ai_model="gpt-4o", retries=2)

    assert result.predicted_answer is None
    assert result.confidence == 0.0
    assert "Couldn't parse" in result.reasoning
