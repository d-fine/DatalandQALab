import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
<<<<<<< HEAD
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
=======

from dataland_qa_lab.review.exceptions import (
    DataCollectionError,
    DatasetNotFoundError,
    OCRProcessingError,
    ReportSubmissionError,
)
from src.dataland_qa_lab.review.dataset_reviewer import review_dataset, review_dataset_via_api


@pytest.fixture
def mock_dependencies() -> Generator[dict[str, MagicMock], None, None]:
    with (
        patch("src.dataland_qa_lab.review.dataset_reviewer.dataset_provider") as mock_dataset_provider,
        patch("src.dataland_qa_lab.review.dataset_reviewer.get_entity") as mock_get_entity,
        patch("src.dataland_qa_lab.review.dataset_reviewer.add_entity") as mock_add_entity,
        patch("src.dataland_qa_lab.review.dataset_reviewer.delete_entity") as mock_delete_entity,
        patch("src.dataland_qa_lab.review.dataset_reviewer.update_reviewed_dataset_in_database") as mock_update_db,
        patch("src.dataland_qa_lab.review.dataset_reviewer.pages_provider") as mock_pages_provider,
        patch("src.dataland_qa_lab.review.dataset_reviewer.text_to_doc_intelligence") as mock_text_to_doc,
        patch("src.dataland_qa_lab.review.dataset_reviewer.NuclearAndGasReportGenerator") as mock_report_gen,
        patch("src.dataland_qa_lab.review.dataset_reviewer.send_alert_message") as mock_send_alert,
        patch("src.dataland_qa_lab.review.dataset_reviewer.get_german_time_as_string") as mock_time,
        patch("src.dataland_qa_lab.review.dataset_reviewer.config") as mock_config,
        patch("src.dataland_qa_lab.review.dataset_reviewer.NuclearAndGasDataCollection") as mock_data_collection,
    ):
        yield {
            "dataset_provider": mock_dataset_provider,
            "get_entity": mock_get_entity,
            "add_entity": mock_add_entity,
            "delete_entity": mock_delete_entity,
            "update_reviewed_dataset_in_database": mock_update_db,
            "pages_provider": mock_pages_provider,
            "text_to_doc_intelligence": mock_text_to_doc,
            "NuclearAndGasReportGenerator": mock_report_gen,
            "send_alert_message": mock_send_alert,
            "get_german_time_as_string": mock_time,
            "config": mock_config,
            "NuclearAndGasDataCollection": mock_data_collection,
        }


def test_review_dataset_creates_new_report(mock_dependencies: dict[str, MagicMock]) -> None:
    """Test creating a new report when none exists."""
    data_id = "test123"

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
    mock_response.qa_report_id = "report_123"

    mock_config_client = mock_dependencies[
        "config"
    ].get_config.return_value.dataland_client.eu_taxonomy_nuclear_gas_qa_api

    mock_config_client.post_nuclear_and_gas_data_qa_report.return_value = mock_response

    result = review_dataset(data_id)

    assert result == "report_123"
    mock_dependencies["add_entity"].assert_called_once()
    mock_dependencies["update_reviewed_dataset_in_database"].assert_called_once_with(
        data_id=data_id, report_id="report_123"
    )
    mock_dependencies["send_alert_message"].assert_any_call(
        message=f"🔍 Starting review of the Dataset with the Data-ID: {data_id}"
    )
    mock_dependencies["send_alert_message"].assert_any_call(
        message=f"✅ Review is successful for the dataset with the Data-ID: {data_id}. Report ID: report_123"
>>>>>>> origin/main
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


<<<<<<< HEAD
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
=======
            assert result == expected


def test_review_dataset_raises_dataset_not_found(mock_dependencies: dict[str, MagicMock]) -> None:
    """DatasetNotFoundERRor is thrown if the dataset is not found."""
    data_id = "missing-id"

    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = None

    with pytest.raises(DatasetNotFoundError):
        review_dataset(data_id)


def test_review_dataset_raises_data_collection_error(mock_dependencies: dict[str, MagicMock]) -> None:
    """Error in NuclearAndGasDataCollection leads to DataCollectionError."""
    data_id = "data-id-collection-error"

    mock_dataset = MagicMock()
    mock_dataset.data = "dummy_data"
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = mock_dataset

    mock_dependencies["get_entity"].return_value = None

    mock_dependencies["NuclearAndGasDataCollection"].side_effect = Exception("boom")

    with pytest.raises(DataCollectionError):
        review_dataset(data_id)


def test_review_dataset_raises_ocr_processing_error(mock_dependencies: dict[str, MagicMock]) -> None:
    """Error at OCR/Text-Extraction leads to OCRProcessingError."""
    data_id = "data-id-ocr-error"

    mock_dataset = MagicMock()
    mock_dataset.data = "dummy_data"
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = mock_dataset
    mock_dependencies["get_entity"].return_value = None

    mock_data_collection_instance = MagicMock()
    mock_dependencies["NuclearAndGasDataCollection"].return_value = mock_data_collection_instance

    mock_dependencies["pages_provider"].get_relevant_page_numbers.return_value = [1, 2]
    mock_dependencies["pages_provider"].get_relevant_pages_of_pdf.return_value = MagicMock()

    mock_dependencies["text_to_doc_intelligence"].get_markdown_from_dataset.side_effect = Exception("ocr fail")

    with pytest.raises(OCRProcessingError):
        review_dataset(data_id)


def test_review_dataset_raises_report_submission_error(mock_dependencies: dict[str, MagicMock]) -> None:
    """An Error occurs by posting the QA-Reports and leads to a ReportSubmissionError."""
    data_id = "data-id-post-error"

    mock_dataset = MagicMock()
    mock_dataset.data = "dummy_data"
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = mock_dataset
    mock_dependencies["get_entity"].return_value = None

    mock_data_collection_instance = MagicMock()
    mock_dependencies["NuclearAndGasDataCollection"].return_value = mock_data_collection_instance
    mock_dependencies["pages_provider"].get_relevant_page_numbers.return_value = []
    mock_dependencies["pages_provider"].get_relevant_pages_of_pdf.return_value = None

    mock_report_instance = MagicMock()
    mock_dependencies["NuclearAndGasReportGenerator"].return_value.generate_report.return_value = mock_report_instance

    mock_client = mock_dependencies["config"].get_config.return_value.dataland_client.eu_taxonomy_nuclear_gas_qa_api
    mock_client.post_nuclear_and_gas_data_qa_report.side_effect = Exception("post fail")

    with pytest.raises(ReportSubmissionError):
        review_dataset(data_id)
>>>>>>> origin/main
