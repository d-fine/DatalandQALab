import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.review.dataset_reviewer import _get_file_using_ocr, validate_datapoint  # noqa: PLC2701


def fake_dp(
    dp_id: str,  # noqa: ARG001
    dp_type: str = "extendedDecimalEstimatedScope1GhgEmissionsInTonnes",
    value: str = "ABC",
    page: int = 1,
) -> SimpleNamespace:
    """Create a fake Dataland data point object."""
    return SimpleNamespace(
        data_point_type=dp_type,
        data_point=json.dumps(
            {"dataSource": {"page": page, "fileReference": "ref1", "fileName": "f.pdf"}, "value": value}
        ),
    )


@patch("dataland_qa_lab.review.dataset_reviewer.config")
@patch("dataland_qa_lab.review.dataset_reviewer.ai.execute_prompt")
@patch("dataland_qa_lab.review.dataset_reviewer._get_file_using_ocr")
def test_validate_datapoint_accept(mock_ocr: MagicMock, mock_ai: MagicMock, mock_config: MagicMock) -> None:
    """Test ACCEPT case when predicted_answer == previous_answer."""
    mock_ocr.return_value = "OCR TEXT"
    mock_ai.return_value = {"answer": "ABC", "confidence": 0.9, "reasoning": "Matches"}

    dp = fake_dp("dp1", dp_type="extendedDecimalEstimatedScope1GhgEmissionsInTonnes", value="ABC")

    # Mock prompt
    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp
    mock_config.validation_prompts = {
        "extendedDecimalEstimatedScope1GhgEmissionsInTonnes": {"prompt": "Check: {context}"}
    }

    result = validate_datapoint("dp1", ai_model="gpt-4o", use_ocr=True)

    assert result.data_point_id == "dp1"
    assert result.qa_status == QaStatus.ACCEPTED
    assert result.predicted_answer == "ABC"


@patch("dataland_qa_lab.review.dataset_reviewer.config")
@patch("dataland_qa_lab.review.dataset_reviewer.ai.execute_prompt")
@patch("dataland_qa_lab.review.dataset_reviewer._get_file_using_ocr")
def test_validate_datapoint_reject(mock_ocr: MagicMock, mock_ai: MagicMock, mock_config: MagicMock) -> None:
    """Test REJECT case when predicted_answer != previous_answer."""
    mock_ocr.return_value = "OCR TEXT"
    mock_ai.return_value = {"answer": "WRONG", "confidence": 0.4, "reasoning": "Different"}

    dp = fake_dp("dp2", dp_type="extendedDecimalEstimatedScope1GhgEmissionsInTonnes", value="CORRECT")

    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp
    mock_config.validation_prompts = {
        "extendedDecimalEstimatedScope1GhgEmissionsInTonnes": {"prompt": "Check: {context}"}
    }

    result = validate_datapoint("dp2", ai_model="gpt-4o")

    assert result.qa_status == QaStatus.REJECTED
    assert result.predicted_answer == "WRONG"


@patch("dataland_qa_lab.review.dataset_reviewer.config")
@patch("dataland_qa_lab.review.dataset_reviewer.ai.execute_prompt")
@patch("dataland_qa_lab.review.dataset_reviewer._get_file_using_ocr")
def test_validate_datapoint_override_calls_change_status(
    mock_ocr: MagicMock, mock_ai: MagicMock, mock_config: MagicMock
) -> None:
    """Test that when override=True, change_data_point_qa_status is called."""
    mock_ocr.return_value = "OCR TEXT"
    mock_ai.return_value = {"answer": "X", "confidence": 0.5, "reasoning": "Test reason"}

    dp = fake_dp("dpX", dp_type="extendedDecimalEstimatedScope1GhgEmissionsInTonnes", value="X")

    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp
    mock_config.validation_prompts = {
        "extendedDecimalEstimatedScope1GhgEmissionsInTonnes": {"prompt": "Prompt {context}"}
    }

    validate_datapoint("dpX", ai_model="gpt-4o", override=True)

    mock_config.dataland_client.qa_api.change_data_point_qa_status.assert_called_once()

    args, kwargs = mock_config.dataland_client.qa_api.change_data_point_qa_status.call_args

    assert args[0] == "dpX"

    assert kwargs["qa_status"] == QaStatus.ACCEPTED
    assert "reason" in kwargs["comment"].lower()


@patch("dataland_qa_lab.review.dataset_reviewer.config")
def test_validate_datapoint_no_prompt_raises(mock_config: MagicMock) -> None:
    """Test that ValueError is raised when no prompt is found for data point type."""
    dp = fake_dp("dp3", dp_type="UNKNOWN_TYPE")
    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp

    mock_config.validation_prompts = {}

    with pytest.raises(ValueError):  # noqa: PT011
        validate_datapoint("dp3", ai_model="gpt-4o")


@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.get_entity")
@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.add_entity")
@patch("dataland_qa_lab.review.dataset_reviewer.text_to_doc_intelligence.extract_pdf")
@patch("dataland_qa_lab.review.dataset_reviewer._get_document")
@patch("dataland_qa_lab.review.dataset_reviewer.config")
def test_get_file_using_ocr_uses_cache(
    mock_config: MagicMock,  # noqa: ARG001
    mock_get_document: MagicMock,
    mock_extract_pdf: MagicMock,
    mock_add: MagicMock,
    mock_get: MagicMock,
) -> None:
    """If CachedDocument exists, it should return its OCR output."""
    mock_get.return_value = SimpleNamespace(ocr_output="CACHED_OCR")

    output = _get_file_using_ocr("file.pdf", "ref123", 2)

    assert output == "CACHED_OCR"
    mock_get_document.assert_not_called()
    mock_extract_pdf.assert_not_called()
    mock_add.assert_not_called()


@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.get_entity", return_value=None)
@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.add_entity")
@patch("dataland_qa_lab.review.dataset_reviewer.text_to_doc_intelligence.extract_pdf")
@patch("dataland_qa_lab.review.dataset_reviewer._get_document")
@patch("dataland_qa_lab.review.dataset_reviewer.config")
def test_get_file_using_ocr_generates_new_ocr(
    mock_config: MagicMock,  # noqa: ARG001
    mock_get_document: MagicMock,
    mock_extract_pdf: MagicMock,
    mock_add: MagicMock,
    mock_get: MagicMock,  # noqa: ARG001
) -> None:
    """When no cache exists, OCR should be generated and added to DB."""
    mock_extract_pdf.return_value = "NEW_OCR"
    mock_get_document.return_value = b"FAKE PDF"

    out = _get_file_using_ocr("file.pdf", "ref123", 5)

    assert out == "NEW_OCR"
    mock_add.assert_called_once()
    mock_extract_pdf.assert_called_once()
    mock_get_document.assert_called_once()
