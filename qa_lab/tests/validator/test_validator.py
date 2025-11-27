from unittest.mock import MagicMock, patch

import pytest

from qa_lab.dataland.api import QaStatus
from qa_lab.validator.validator import get_file_using_ocr, validate_datapoint

DUMMY_FILE = b"%PDF-1.4 dummy content"


@patch("qa_lab.validator.validator.get_entity")
def test_get_file_using_ocr_cached(mock_get_entity: MagicMock) -> None:
    """Test get_file_using_ocr when document is cached."""
    cached_doc = MagicMock(ocr_output="cached text")
    mock_get_entity.return_value = cached_doc

    result = get_file_using_ocr("file.pdf", "ref1", 1)
    assert result == "cached text"
    mock_get_entity.assert_called_once()


@patch("qa_lab.validator.validator.add_entity")
@patch("qa_lab.validator.validator.extract_pdf")
@patch("qa_lab.validator.validator.get_document")
@patch("qa_lab.validator.validator.get_entity", return_value=None)
def test_get_file_using_ocr_not_cached(
    mock_get_entity: MagicMock,  # noqa: ARG001
    mock_get_document: MagicMock,
    mock_extract_pdf: MagicMock,
    mock_add_entity: MagicMock,
) -> None:
    """Test get_file_using_ocr when document is not cached."""
    mock_get_document.return_value = DUMMY_FILE
    mock_extract_pdf.return_value = "extracted text"

    result = get_file_using_ocr("file.pdf", "ref1", 1)
    assert result == "extracted text"
    mock_add_entity.assert_called_once()


@patch("qa_lab.validator.validator.update_data_point_qa_report")
@patch("qa_lab.validator.validator.execute_prompt")
@patch("qa_lab.validator.validator.get_file_using_ocr")
@patch("qa_lab.validator.validator.get_data_point")
@patch("qa_lab.validator.validator.prompts", {"TestType": {"prompt": "Check this: {context}"}})
def test_validate_datapoint_accepted(
    mock_get_data_point: MagicMock, mock_get_file: MagicMock, mock_execute_prompt: MagicMock, mock_update: MagicMock
) -> None:
    """Test that validate_datapoint correctly identifies accepted answers."""
    mock_get_data_point.return_value = {
        "dataPointType": "TestType",
        "dataPoint": {"value": "42", "dataSource": {"fileReference": "ref1", "fileName": "file.pdf", "page": 1}},
    }
    mock_get_file.return_value = "some markdown"
    mock_execute_prompt.return_value = {"answer": "42", "confidence": 1.0, "reasoning": "Correct"}

    result = validate_datapoint("dp1", ai_model="test-model", use_ocr=True, override=True)

    assert result["qa_status"] == QaStatus.Accepted
    assert result["predicted_answer"] == "42"
    mock_update.assert_called_once()


@patch("qa_lab.validator.validator.update_data_point_qa_report")
@patch("qa_lab.validator.validator.execute_prompt")
@patch("qa_lab.validator.validator.get_file_using_ocr")
@patch("qa_lab.validator.validator.get_data_point")
@patch("qa_lab.validator.validator.prompts", {"TestType": {"prompt": "Check this: {context}"}})
def test_validate_datapoint_rejected(
    mock_get_data_point: MagicMock, mock_get_file: MagicMock, mock_execute_prompt: MagicMock, mock_update: MagicMock
) -> None:
    """Test that validate_datapoint correctly identifies rejected answers."""
    mock_get_data_point.return_value = {
        "dataPointType": "TestType",
        "dataPoint": {"value": "42", "dataSource": {"fileReference": "ref1", "fileName": "file.pdf", "page": 1}},
    }
    mock_get_file.return_value = "some markdown"
    mock_execute_prompt.return_value = {"answer": "24", "confidence": 0.9, "reasoning": "Incorrect"}

    result = validate_datapoint("dp1", ai_model="test-model", use_ocr=True, override=True)

    assert result["qa_status"] == QaStatus.Rejected
    assert result["predicted_answer"] == "24"
    mock_update.assert_called_once()


def test_validate_datapoint_no_prompt() -> None:
    """Test that ValueError is raised when no prompt is found for data point type."""
    with (
        patch("qa_lab.validator.validator.get_data_point") as mock_get_data_point,
        patch("qa_lab.validator.validator.prompts", {}),
    ):
        mock_get_data_point.return_value = {"dataPointType": "UnknownType", "dataPoint": {}}

        with pytest.raises(ValueError, match="No prompt found for data point type: UnknownType"):
            validate_datapoint("dp1", ai_model="test-model")
