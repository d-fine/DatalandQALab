import time
from unittest.mock import MagicMock, patch

import pytest
from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import db as db_module
from dataland_qa_lab.data_point_flow import models
from dataland_qa_lab.database import database_tables


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.db.database_engine")
async def test_store_data_point_in_db_validated(mock_db_engine: MagicMock) -> None:
    """Test storing a ValidatedDatapoint in the database."""
    data = models.ValidatedDatapoint(
        data_point_id="dp123",
        data_point_type="number",
        previous_answer=10,
        predicted_answer=12,
        confidence=0.9,
        reasoning="Reasoning text",
        qa_status=QaStatus.ACCEPTED,
        timestamp=int(time.time()),
        ai_model="gpt-4",
        use_ocr=False,
        file_name="file.pdf",
        file_reference="ref123",
        page=1,
        override=None,
    )

    await db_module.store_data_point_in_db(data)

    mock_db_engine.add_entity.assert_called_once()
    added_entity = (
        mock_db_engine.add_entity.call_args.kwargs.get("entity") or mock_db_engine.add_entity.call_args.args[0]
    )
    assert added_entity.data_point_id == "dp123"
    assert added_entity.predicted_answer == 12
    assert added_entity.qa_status == QaStatus.ACCEPTED


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.db.database_engine")
async def test_store_data_point_in_db_cannot_validate(mock_db_engine: MagicMock) -> None:
    """Test storing a CannotValidateDatapoint in the database."""
    data = models.CannotValidateDatapoint(
        data_point_id="dp456",
        data_point_type="number",
        reasoning="Cannot validate",
        ai_model="gpt-4",
        use_ocr=True,
        override=None,
        timestamp=int(time.time()),
    )

    await db_module.store_data_point_in_db(data)

    added_entity = mock_db_engine.add_entity.call_args[0][0]
    assert added_entity.data_point_id == "dp456"
    assert added_entity.predicted_answer is None
    assert added_entity.confidence == 0.0
    assert added_entity.qa_status == "NotAttempted"


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.db.database_engine")
async def test_check_if_already_validated_none(mock_db_engine: MagicMock) -> None:
    """Test when no existing validation is found."""
    mock_db_engine.get_entity.return_value = None

    result = await db_module.check_if_already_validated("dp123")
    assert result is None


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.db.database_engine")
async def test_check_if_already_validated_validated(mock_db_engine: MagicMock) -> None:
    """Test returning a ValidatedDatapoint if already validated."""
    mock_entity = MagicMock()
    mock_entity.data_point_id = "dp123"
    mock_entity.data_point_type = "number"
    mock_entity.previous_answer = 10
    mock_entity.predicted_answer = 12
    mock_entity.confidence = 0.9
    mock_entity.reasoning = "Reasoning text"
    mock_entity.qa_status = QaStatus.ACCEPTED
    mock_entity.timestamp = int(time.time())
    mock_entity.ai_model = "gpt-4"
    mock_entity.use_ocr = False
    mock_entity.file_name = "file.pdf"
    mock_entity.file_reference = "ref123"
    mock_entity.page = 1

    mock_db_engine.get_entity.return_value = mock_entity

    result = await db_module.check_if_already_validated("dp123")
    assert isinstance(result, models.ValidatedDatapoint)
    assert result.data_point_id == "dp123"
    assert result.predicted_answer == 12


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.db.database_engine")
async def test_check_if_already_validated_cannot_validate(mock_db_engine: MagicMock) -> None:
    """Test returning a CannotValidateDatapoint if predicted_answer is None."""
    mock_entity = MagicMock()
    mock_entity.data_point_id = "dp123"
    mock_entity.data_point_type = "number"
    mock_entity.predicted_answer = None
    mock_entity.reasoning = "Cannot validate"
    mock_entity.ai_model = "gpt-4"
    mock_entity.use_ocr = False
    mock_entity.timestamp = int(time.time())

    mock_db_engine.get_entity.return_value = mock_entity

    result = await db_module.check_if_already_validated("dp123")
    assert isinstance(result, models.CannotValidateDatapoint)
    assert result.data_point_id == "dp123"
    assert result.reasoning == "Cannot validate"


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.db.database_engine")
async def test_delete_existing_entry_calls_delete(mock_db_engine: MagicMock) -> None:
    """Test that delete_existing_entry calls delete_entity."""
    await db_module.delete_existing_entry("dp123")
    mock_db_engine.delete_entity.assert_called_once_with(
        entity_id="dp123", entity_class=database_tables.ValidatedDataPoint
    )
