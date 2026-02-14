"""Tests for false positive detection in QA validation.

This module tests that the QA system correctly rejects data points
when the AI's predicted answer differs from the previous answer.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dataland_qa_lab.data_point_flow.ai import execute_prompt


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_qa_rejected_when_answers_differ(mock_client: MagicMock) -> None:
    """Test that QaRejected is returned when predicted_answer differs from previous_answer."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "predicted_answer": "No",
                        "confidence": 0.95,
                        "reasoning": "The document clearly states No",
                        "qa_status": "QaRejected",
                    }
                )
            )
        )
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await execute_prompt(
        prompt="Is nuclear energy used?",
        previous_answer="Yes",
        ai_model="gpt-4o",
    )

    assert result.predicted_answer == "No"
    assert result.qa_status == "QaRejected"


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_qa_accepted_when_answers_match(mock_client: MagicMock) -> None:
    """Test that QaAccepted is returned when predicted_answer matches previous_answer."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "predicted_answer": "Yes",
                        "confidence": 0.95,
                        "reasoning": "The document confirms Yes",
                        "qa_status": "QaAccepted",
                    }
                )
            )
        )
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await execute_prompt(
        prompt="Is nuclear energy used?",
        previous_answer="Yes",
        ai_model="gpt-4o",
    )

    assert result.predicted_answer == "Yes"
    assert result.qa_status == "QaAccepted"


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_qa_rejected_for_decimal_mismatch(mock_client: MagicMock) -> None:
    """Test that QaRejected is returned when decimal values differ."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "predicted_answer": "42.5",
                        "confidence": 0.9,
                        "reasoning": "Document shows 42.5",
                        "qa_status": "QaRejected",
                    }
                )
            )
        )
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await execute_prompt(
        prompt="What is the revenue?",
        previous_answer="999",
        ai_model="gpt-4o",
    )

    assert result.predicted_answer == "42.5"
    assert result.qa_status == "QaRejected"


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_previous_answer_included_in_prompt(mock_client: MagicMock) -> None:
    """Test that the previous_answer is included in the prompt sent to AI."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "predicted_answer": "Yes",
                        "confidence": 0.9,
                        "reasoning": "Test",
                        "qa_status": "QaAccepted",
                    }
                )
            )
        )
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    await execute_prompt(
        prompt="Test prompt",
        previous_answer="TestPreviousAnswer",
        ai_model="gpt-4o",
    )

    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    user_content = messages[1]["content"][0]["text"]

    assert "Previous Answer to compare against: TestPreviousAnswer" in user_content


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("previous_answer", "predicted_answer", "expected_status"),
    [
        ("Yes", "No", "QaRejected"),
        ("No", "Yes", "QaRejected"),
        ("Yes", "Yes", "QaAccepted"),
        ("No", "No", "QaAccepted"),
    ],
)
@patch("dataland_qa_lab.data_point_flow.ai.client")
async def test_yes_no_comparison_logic(
    mock_client: MagicMock,
    previous_answer: str,
    predicted_answer: str,
    expected_status: str,
) -> None:
    """Test Yes/No comparison returns correct QA status."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "predicted_answer": predicted_answer,
                        "confidence": 0.95,
                        "reasoning": "Test reasoning",
                        "qa_status": expected_status,
                    }
                )
            )
        )
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await execute_prompt(
        prompt="Test question",
        previous_answer=previous_answer,
        ai_model="gpt-4o",
    )

    assert result.qa_status == expected_status
