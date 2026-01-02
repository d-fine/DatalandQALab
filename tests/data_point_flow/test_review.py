import contextlib
import io
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import models
from dataland_qa_lab.data_point_flow import review as validate


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.review.db")
async def test_already_validated_no_override(mock_db: MagicMock) -> None:
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
        _prompt="prompt text",
    )

    mock_db.check_if_already_validated = AsyncMock(return_value=existing)

    result = await validate.validate_datapoint("dp123", use_ocr=True, ai_model="gpt-4", override=False)
    assert result == existing
    mock_db.delete_existing_entry.assert_not_called()


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.review.db")
@patch("dataland_qa_lab.data_point_flow.review.dataland")
async def test_data_point_fetch_fails(mock_dataland: MagicMock, mock_db: MagicMock) -> None:
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
async def test_no_prompt_configured(mock_prompts: MagicMock, mock_dataland: MagicMock, mock_db: MagicMock) -> None:
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
) -> None:
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
    mock_db.store_data_point_in_db.assert_called_once()
    mock_dataland.override_dataland_qa.assert_called_once()


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.review.db")
async def test_override_existing_entry(mock_db: MagicMock) -> None:
    """Deletes existing entry if override=True and re-validates."""
    mock_db.check_if_already_validated = AsyncMock(return_value=MagicMock())
    mock_db.delete_existing_entry = AsyncMock()

    mock_db.store_data_point_in_db = AsyncMock()

    with (
        patch("dataland_qa_lab.data_point_flow.review.dataland.get_data_point", side_effect=ValueError("Stop")),
        contextlib.suppress(ValueError),
    ):
        await validate.validate_datapoint("dp123", use_ocr=True, ai_model="gpt-4", override=True)
    mock_db.delete_existing_entry.assert_awaited_once_with("dp123")


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.review.config")
@patch("dataland_qa_lab.data_point_flow.review.db")
@patch("dataland_qa_lab.data_point_flow.review.dataland")
@patch("dataland_qa_lab.data_point_flow.review.prompts")
@patch("dataland_qa_lab.data_point_flow.review.pdf_handler")
@patch("dataland_qa_lab.data_point_flow.review.image_helper")
@patch("dataland_qa_lab.data_point_flow.review.ai")
async def test_vision_flow(  # noqa: PLR0913, PLR0917
    mock_ai: MagicMock,
    mock_img_helper: MagicMock,
    mock_pdf_handler: MagicMock,
    mock_prompts: MagicMock,
    mock_dataland: MagicMock,
    mock_db: MagicMock,
    mock_config: MagicMock,
) -> None:
    """Tests validation workflow for bypassing OCR and using image-based AI."""
    mock_config.get_config.return_value.vision_enabled = True
    mock_config.vision.enabled = True
    mock_config.vision.dpi = 300
    mock_db.check_if_already_validated = AsyncMock(return_value=None)
    mock_db.store_data_point_in_db = AsyncMock()
    mock_dataland.get_data_point = AsyncMock(return_value=MagicMock(value="A", file_reference="ref", page=1))
    mock_dataland.get_document = AsyncMock(return_value=io.BytesIO(b"pdf content"))
    mock_dataland.override_dataland_qa = AsyncMock()
    mock_prompts.get_prompt_config.return_value = MagicMock(prompt="What is shown? {context}")

    mock_pdf_handler.render_pdf_to_image.return_value = ["image"]
    mock_img_helper.encode_image_to_base64.return_value = "base64image"

    mock_ai.execute_prompt = AsyncMock(
        return_value=MagicMock(predicted_answer="A", confidence=0.95, reasoning="Correct")
    )

    await validate.validate_datapoint("dp_vision", use_ocr=False, ai_model="gpt-vision", override=False)
    mock_pdf_handler.render_pdf_to_image.assert_called()


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.review.config")
@patch("dataland_qa_lab.data_point_flow.review.db")
@patch("dataland_qa_lab.data_point_flow.review.dataland")
@patch("dataland_qa_lab.data_point_flow.review.prompts")
async def test_vision_flow_vision_disabled(
    mock_prompts: MagicMock,
    mock_dataland: MagicMock,
    mock_db: MagicMock,
    mock_config: MagicMock,
) -> None:
    """Tests that RuntimeError is raised if vision is disabled in config."""
    mock_config.vision.enabled = False
    mock_config.vision.dpi = 300
    mock_db.check_if_already_validated = AsyncMock(return_value=None)
    mock_db.store_data_point_in_db = AsyncMock()
    mock_dataland.get_data_point = AsyncMock(return_value=MagicMock(value="A", file_reference="ref", page=1))
    mock_dataland.get_document = AsyncMock(return_value=io.BytesIO(b"pdf content"))
    mock_prompts.get_prompt_config.return_value = MagicMock(prompt="What is shown? {context}")

    result = await validate.validate_datapoint("dp_vision", use_ocr=False, ai_model="gpt-vision", override=False)

    assert isinstance(result, models.CannotValidateDatapoint)


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.review.config")
@patch("dataland_qa_lab.data_point_flow.review.db")
@patch("dataland_qa_lab.data_point_flow.review.dataland")
@patch("dataland_qa_lab.data_point_flow.review.prompts")
@patch("dataland_qa_lab.data_point_flow.review.pdf_handler")
@patch("dataland_qa_lab.data_point_flow.review.ai")
async def test_vision_flow_no_images_rendered(  # noqa: PLR0913, PLR0917
    mock_ai: MagicMock,
    mock_pdf_handler: MagicMock,
    mock_prompts: MagicMock,
    mock_dataland: MagicMock,
    mock_db: MagicMock,
    mock_config: MagicMock,
) -> None:
    """Test that VaulueError is raised if no images are rendered from PDF."""
    mock_config.vision.enabled = True
    mock_config.vision.dpi = 300
    mock_db.check_if_already_validated = AsyncMock(return_value=None)
    mock_db.store_data_point_in_db = AsyncMock()
    mock_dataland.get_data_point = AsyncMock(
        return_value=MagicMock(data_point_type="img", value="v", file_reference="ref", page=1)
    )
    mock_prompts.get_prompt_config.return_value = MagicMock(prompt="What is shown? {context}")
    mock_dataland.get_document = AsyncMock(return_value=io.BytesIO(b"pdf content"))
    mock_dataland.override_dataland_qa = AsyncMock()

    mock_pdf_handler.render_pdf_to_image.return_value = []
    mock_ai.execute_prompt.side_effect = Exception("No images were rendered from the PDF document.")
    result = await validate.validate_datapoint("dp_no_images", use_ocr=False, ai_model="gpt-vision", override=False)
    assert isinstance(result, models.CannotValidateDatapoint)
    assert "No images were rendered from the PDF document." in result.reasoning


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.review.db")
@patch("dataland_qa_lab.data_point_flow.review.dataland")
@patch("dataland_qa_lab.data_point_flow.review.prompts")
@patch("dataland_qa_lab.data_point_flow.review.ocr")
async def test_processing_exception_handling(
    mock_ocr: MagicMock, mock_prompts: MagicMock, mock_dataland: MagicMock, mock_db: MagicMock
) -> None:
    """Test that exceptions during processing return CannotValidateDatapoint."""
    mock_db.check_if_already_validated = AsyncMock(return_value=None)
    mock_db.store_data_point_in_db = AsyncMock()
    mock_dataland.get_data_point = AsyncMock(
        return_value=MagicMock(data_point_type="any", value="v", file_reference="ref", page=1)
    )
    mock_prompts.get_prompt_config.return_value = MagicMock()
    mock_dataland.get_document = AsyncMock(return_value=io.BytesIO(b"pdf"))

    mock_ocr.run_ocr_on_document.side_effect = Exception("Fatal OCR Crash")

    result = await validate.validate_datapoint("dp1", use_ocr=True, ai_model="gpt", override=False)

    assert isinstance(result, models.CannotValidateDatapoint)
    assert "Processing failed" in result.reasoning
    assert "Fatal OCR Crash" in result.reasoning


@pytest.mark.asyncio
async def test_fetch_dependency_datapoints_returns_expected_context() -> None:
    """Test that fetch_dependency_datapoints returns the expected context string."""
    dataset_id = "dataset_123"
    depends_on = ["type_a", "type_b"]
    use_ocr = True
    ai_model = "gpt-test"

    mocked_data_points = {"type_a": "dp_a_1", "type_b": "dp_b_2", "type_c": "dp_c_3"}

    mocked_validation_a = {"id": "dp_a_1", "validated": True}
    mocked_validation_b = {"id": "dp_b_2", "validated": True}

    with (
        patch(
            "dataland_qa_lab.data_point_flow.review.dataland.get_contained_data_points", new_callable=AsyncMock
        ) as mock_get,
        patch("dataland_qa_lab.data_point_flow.review.validate_datapoint", new_callable=AsyncMock) as mock_validate,
        patch("dataland_qa_lab.data_point_flow.review.asdict", side_effect=lambda x: x),
    ):
        mock_get.return_value = mocked_data_points
        mock_validate.side_effect = [mocked_validation_a, mocked_validation_b]

        result = await validate.fetch_dependency_datapoints(
            dataset_id=dataset_id, depends_on=depends_on, use_ocr=use_ocr, ai_model=ai_model
        )

        expected_output = ""
        for dtype, val in zip(depends_on, [mocked_validation_a, mocked_validation_b], strict=False):
            expected_output += f"This is the validated output for the data point of type {dtype}:\n"
            expected_output += json.dumps(val)
            expected_output += "\n"

        assert result == expected_output
        mock_get.assert_awaited_once_with(dataset_id)
        assert mock_validate.await_count == 2


@pytest.mark.asyncio
async def test_fetch_dependency_datapoints_skips_missing_datapoints() -> None:
    """Test that missing dependency datapoints are skipped."""
    dataset_id = "dataset_456"
    depends_on = ["type_x", "type_y"]
    use_ocr = False
    ai_model = "gpt-test-2"

    mocked_data_points = {"type_x": "dp_x_1"}

    mocked_validation_x = {"id": "dp_x_1", "validated": True}

    with (
        patch(
            "dataland_qa_lab.data_point_flow.review.dataland.get_contained_data_points", new_callable=AsyncMock
        ) as mock_get,
        patch("dataland_qa_lab.data_point_flow.review.validate_datapoint", new_callable=AsyncMock) as mock_validate,
        patch("dataland_qa_lab.data_point_flow.review.asdict", side_effect=lambda x: x),
    ):
        mock_get.return_value = mocked_data_points
        mock_validate.return_value = mocked_validation_x

        result = await validate.fetch_dependency_datapoints(
            dataset_id=dataset_id, depends_on=depends_on, use_ocr=use_ocr, ai_model=ai_model
        )

        expected_output = "This is the validated output for the data point of type type_x:\n"
        expected_output += json.dumps(mocked_validation_x)
        expected_output += "\n"

        assert result == expected_output
        mock_get.assert_awaited_once_with(dataset_id)
        mock_validate.assert_awaited_once_with(
            data_point_id="dp_x_1",
            use_ocr=use_ocr,
            ai_model=ai_model,
            override=False,
            dataset_id=dataset_id,
        )
