import json
from collections.abc import Generator
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from dataland_qa_lab.database import database_tables
from dataland_qa_lab.review.dataset_reviewer import (
    _get_file_using_ocr,  # noqa: PLC2701
    old_review_dataset,
    update_error_reason_in_database,
    validate_datapoint,
)
from dataland_qa_lab.review.exceptions import DatasetNotFoundError, OCRProcessingError


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


@pytest.fixture
def mock_dependencies() -> Generator[dict[str, MagicMock], None, None]:
    with (
        patch("dataland_qa_lab.review.dataset_reviewer.dataset_provider") as mock_dataset_provider,
        patch("dataland_qa_lab.review.dataset_reviewer.database_engine.get_entity") as mock_get_entity,
        patch("dataland_qa_lab.review.dataset_reviewer.database_engine.add_entity") as mock_add_entity,
        patch("dataland_qa_lab.review.dataset_reviewer.database_engine.delete_entity") as mock_delete_entity,
        patch("dataland_qa_lab.review.dataset_reviewer.old_update_reviewed_dataset_in_database") as mock_update_db,
        patch("dataland_qa_lab.review.dataset_reviewer.pages_provider") as mock_pages_provider,
        patch("dataland_qa_lab.review.dataset_reviewer.text_to_doc_intelligence") as mock_text_to_doc,
        patch("dataland_qa_lab.review.dataset_reviewer.NuclearAndGasReportGenerator") as mock_report_gen,
        patch("dataland_qa_lab.review.dataset_reviewer.slack.send_slack_message") as mock_send_slack,
        patch("dataland_qa_lab.review.dataset_reviewer.get_german_time_as_string") as mock_time,
        patch("dataland_qa_lab.review.dataset_reviewer.config") as mock_config,
        patch("dataland_qa_lab.review.dataset_reviewer.NuclearAndGasDataCollection") as mock_data_collection,
    ):
        yield {
            "dataset_provider": mock_dataset_provider,
            "get_entity": mock_get_entity,
            "add_entity": mock_add_entity,
            "delete_entity": mock_delete_entity,
            "old_update_reviewed_dataset_in_database": mock_update_db,
            "pages_provider": mock_pages_provider,
            "text_to_doc_intelligence": mock_text_to_doc,
            "NuclearAndGasReportGenerator": mock_report_gen,
            "send_slack_message": mock_send_slack,
            "get_german_time_as_string": mock_time,
            "config": mock_config,
            "NuclearAndGasDataCollection": mock_data_collection,
        }


def test_review_dataset_creates_new_report(mock_dependencies: MagicMock) -> None:
    """Test that reviewing a dataset creates a new report when none exists."""
    data_id = "report_123"

    mock_dataset = MagicMock()
    mock_dataset.general = {"some_key": "some_value"}
    mock_dataset.data = "dummy_data"
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = mock_dataset

    mock_dependencies["get_entity"].return_value = None

    mock_dependencies["get_german_time_as_string"].return_value = "2025-11-17T12:00:00"

    mock_data_collection_instance = MagicMock()
    mock_dependencies["NuclearAndGasDataCollection"].return_value = mock_data_collection_instance

    mock_report_instance = MagicMock()
    mock_report_instance.to_json.return_value = json.dumps({"report": "data"})
    mock_dependencies["NuclearAndGasReportGenerator"].return_value.generate_report.return_value = mock_report_instance

    mock_response = MagicMock()
    mock_response.qa_report_id = data_id

    api_client = mock_dependencies["config"].dataland_client.eu_taxonomy_nuclear_gas_qa_api
    api_client.post_nuclear_and_gas_data_qa_report.return_value = mock_response

    result = old_review_dataset(data_id)

    assert result == data_id


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


@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.update_entity")
@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.get_entity")
def test_update_error_reason_sets_reason(
    mock_get_entity: MagicMock,
    mock_upate_entity: MagicMock,
) -> None:
    review_row = SimpleNamespace(error_reason=None)
    mock_get_entity.return_value = review_row

    data_id = "test-id-123"
    error_msg = "Something went wrong"

    update_error_reason_in_database(data_id=data_id, error_reason=error_msg)

    assert review_row.error_reason == error_msg

    mock_upate_entity.assert_called_once_with(review_row)


@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.update_entity")
@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.get_entity")
def test_update_error_reason_no_row_does_not_update(
    mock_get_entity: MagicMock,
    mock_update_entity: MagicMock,
) -> None:
    mock_get_entity.return_value = None

    update_error_reason_in_database(data_id="missing-id", error_reason="irrelevant")

    mock_update_entity.assert_not_called()


def test_old_review_dataset_dataset_missing_updates_error_reason(mock_dependencies: MagicMock) -> None:
    data_id = "missing_id"
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = None

    with patch("dataland_qa_lab.review.dataset_reviewer.update_error_reason_in_database") as mock_update_err:
        with pytest.raises(DatasetNotFoundError):
            old_review_dataset(data_id)

        mock_update_err.assert_called_once()


def test_old_review_dataset_returns_existing_report_id_when_exists(mock_dependencies: MagicMock) -> None:
    data_id = "abc"

    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = MagicMock(data="dummy")
    mock_dependencies["get_entity"].return_value = SimpleNamespace(report_id="Existing_RID")

    result = old_review_dataset(data_id, force_review=False)

    assert result == "Existing_RID"


def test_old_review_dataset_force_review_deletes_old_entries_and_sets_error_reason(
    mock_dependencies: MagicMock,
) -> None:
    data_id = "abc"

    mock_dependencies["dataset_provider"].get_dataste_by_id.return_value = MagicMock(data="dummy")

    mock_dependencies["get_entity"].side_effect = [
        SimpleNamespace(report_id="OLD_RID"),
        SimpleNamespace(),
    ]

    mock_dependencies["NuclearAndGasDataCollection"].return_value = MagicMock()
    mock_dependencies["pages_provider"].get_relevant_page_numbers.return_value = [1]
    mock_dependencies["pages_provider"].get_relevant_pages_of_pdf.return_value = object()

    mock_dependencies["text_to_doc_intelligence"].old_get_markdown_from_dataset.side_effect = Exception("boom")

    with patch("dataland_qa_lab.review.dataset_reviewer.update_error_reason_in_database") as mock_update_err:
        with pytest.raises(OCRProcessingError):
            old_review_dataset(data_id, force_review=True, use_ocr=True, ai_model="gpt-4o")

        mock_dependencies["delete_entity"].assert_any_call(data_id, database_tables.ReviewedDataset)
        mock_dependencies["delete_entity"].assert_any_call(data_id, database_tables.ReviewedDatasetMarkdowns)

        mock_update_err.assert_called_once()
