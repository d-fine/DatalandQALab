import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dataland_qa_lab.data_point_flow.ai import execute_prompt


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_execute_prompt_valid_json(mock_client: MagicMock) -> None:
    """Test that execute_prompt returns correct data on valid JSON response."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {"predicted_answer": "OK", "confidence": 0.9, "reasoning": "All good", "qa_status": "QaAccepted"}
                )
            )
        )
    ]

    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await execute_prompt("test?", previous_answer="test?", ai_model="gpt-4o")

    assert result.predicted_answer == "OK"
    assert result.confidence == 0.9
    assert result.qa_status == "QaAccepted"


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_execute_prompt_retry_on_invalid_json(mock_client: MagicMock) -> None:
    """Test that execute_prompt retries on invalid JSON responses."""

    def make_resp(content: str) -> MagicMock:
        m = MagicMock()
        m.choices = [MagicMock(message=MagicMock(content=content))]
        return m

    mock_client.chat.completions.create = AsyncMock(
        side_effect=[
            make_resp("not json"),
            make_resp("still bad"),
            make_resp(
                json.dumps(
                    {
                        "predicted_answer": "42",
                        "confidence": 0.8,
                        "reasoning": "Finally valid",
                        "qa_status": "QaAccepted",
                    }
                )
            ),
        ]
    )

    result = await execute_prompt("test?", previous_answer="test?", ai_model="gpt-4o", retries=3)

    assert result.predicted_answer == "42"
    assert result.confidence == 0.8
    assert "Finally valid" in result.reasoning


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_execute_prompt_no_content(mock_client: MagicMock) -> None:
    """Test that execute_prompt handles no content response with fallback."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=None))]

    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    # We set retries=0 to avoid the sleep delay in testing the fallback
    result = await execute_prompt("test?", previous_answer="test?", ai_model="gpt-4o", retries=0)

    assert result.predicted_answer is None
    assert result.confidence == 0.0
    assert result.qa_status == "QaInconclusive"
    assert "Empty response" in result.reasoning


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_execute_prompt_exception_retry_exhaustion(mock_client: MagicMock) -> None:
    """Test that execute_prompt falls back after all retries fail via exception."""
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Down"))

    result = await execute_prompt("test?", previous_answer="test?", ai_model="gpt-4o", retries=1)

    assert result.predicted_answer is None
    assert result.qa_status == "QaInconclusive"
    assert "API Down" in result.reasoning
