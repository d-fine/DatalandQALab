import io
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from dataland_qa.models.qa_status import QaStatus
from dataland_qa_lab.data_point_flow import review as validate
from dataland_qa_lab.data_point_flow import models


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.review.db")
async def test_already_validated_no_override(mock_db: MagicMock):
    """Returns existing data point if already validated and override=False."""
    existing = models.ValidatedDatapoint(
        data_point_id="dp123",
        data_point_type="number",
        previous_answer=10,
        predicted_answer=12,
        confidence=0.9,
        reasoning="Already validated",
        qa_status=QaStatus.ACCEPTED,
        timestamp=int(time.time()),
        ai_model="gpt-4",
        use_ocr=True,
        file_name="file.pdf",
        file_reference="ref123",
        page=1,
        override=None,
    )

    # Make check_if_already_validated return a coroutine
    mock_db.check_if_already_validated = AsyncMock(return_value=existing)

    result = await validate.validate_datapoint("dp123", use_ocr=True, ai_model="gpt-4", override=False)
    assert result == existing
    mock_db.delete_existing_entry.assert_not_called()


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.review.db")
@patch("dataland_qa_lab.data_point_flow.review.dataland")
async def test_data_point_fetch_fails(mock_dataland: MagicMock, mock_db: MagicMock):
    """Returns CannotValidateDatapoint if get_data_point raises exception."""
    mock_db.check_if_already_validated = AsyncMock(return_value=None)
    mock_db.store_data_point_in_db = AsyncMock()
    mock_dataland.get_data_point = AsyncMock(side_effect=Exception("API failure"))

    result = await validate.validate_datapoint("dp_fail", use_ocr=True, ai_model="gpt-4", override=False)
    assert isinstance(result, models.CannotValidateDatapoint)
    assert "Couldn't fetch data point" in result.reasoning
    mock_db.store_data_point_in_db.assert_called_once()


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.review.db")
@patch("dataland_qa_lab.data_point_flow.review.dataland")
@patch("dataland_qa_lab.data_point_flow.review.prompts")
async def test_no_prompt_configured(mock_prompts: MagicMock, mock_dataland: MagicMock, mock_db: MagicMock):
    """Returns CannotValidateDatapoint if no prompt is configured for data point type."""
    mock_db.check_if_already_validated = AsyncMock(return_value=None)
    mock_db.store_data_point_in_db = AsyncMock()
    mock_prompts.get_prompt_config.return_value = None
    mock_dataland.get_data_point = AsyncMock(
        return_value=MagicMock(
            data_point_id="dp123",
            data_point_type="unknown_type",
            value=42,
            file_reference="ref123",
            page=1,
            file_name="file.pdf",
        )
    )

    result = await validate.validate_datapoint("dp123", use_ocr=True, ai_model="gpt-4", override=False)
    assert isinstance(result, models.CannotValidateDatapoint)
    assert "No Prompt configured" in result.reasoning
    mock_db.store_data_point_in_db.assert_called_once()


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.review.db")
@patch("dataland_qa_lab.data_point_flow.review.dataland")
@patch("dataland_qa_lab.data_point_flow.review.prompts")
@patch("dataland_qa_lab.data_point_flow.review.ocr")
@patch("dataland_qa_lab.data_point_flow.review.ai")
async def test_full_validation_workflow(
    mock_ai: MagicMock, mock_ocr: MagicMock, mock_prompts: MagicMock, mock_dataland: MagicMock, mock_db: MagicMock
):
    """Tests full validation workflow with OCR and AI."""
    mock_db.check_if_already_validated = AsyncMock(return_value=None)
    mock_db.store_data_point_in_db = AsyncMock()
    mock_dataland.get_data_point = AsyncMock(
        return_value=MagicMock(
            data_point_id="dp123",
            data_point_type="number",
            value="42",
            file_reference="ref123",
            page=1,
            file_name="file.pdf",
        )
    )
    mock_dataland.get_document = AsyncMock(return_value=io.BytesIO(b"pdf content"))
    mock_dataland.override_dataland_qa = AsyncMock()
    mock_prompts.get_prompt_config.return_value = MagicMock(prompt="Answer: {context}")
    mock_ocr.run_ocr_on_document = AsyncMock(return_value="extracted text")
    mock_ai.execute_prompt = AsyncMock(
        return_value=MagicMock(predicted_answer="42", confidence=0.9, reasoning="Matches")
    )

    result = await validate.validate_datapoint("dp123", use_ocr=True, ai_model="gpt-4", override=False)
    assert isinstance(result, models.ValidatedDatapoint)
    assert result.qa_status == QaStatus.ACCEPTED
    mock_db.store_data_point_in_db.assert_called_once()
    mock_dataland.override_dataland_qa.assert_called_once()
