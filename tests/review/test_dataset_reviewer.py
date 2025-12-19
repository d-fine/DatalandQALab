import json
from collections.abc import Generator
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.review.qa_status import QaStatus
from dataland_qa_lab.review.dataset_reviewer import (
    _get_file_using_ocr,  # noqa: PLC2701
    old_review_dataset,
    validate_datapoint,
    validation_prompts,
)
from dataland_qa_lab.review.exceptions import (
    DataCollectionError,
    DatasetNotFoundError,
    OCRProcessingError,
    ReportSubmissionError,
)


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
            {
                "dataSource": {
                    "page": page,
                    "fileReference": "ref1",
                    "fileName": "f.pdf",
                },
                "value": value,
            }
        ),
    )


@pytest.fixture
def mock_dependencies() -> Generator[dict[str, MagicMock], None, None]:
    """This fixture provides mocked dependencies for dataset_reviewer tests."""
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
    """Test reviewing a dataset creates a new report when none exists."""
    data_id = "report_123"

    mock_dataset = MagicMock()
    mock_dataset.data = "dummy_data"
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = mock_dataset
    mock_dependencies["get_entity"].return_value = None
    mock_dependencies["get_german_time_as_string"].return_value = "2025-11-17T12:00:00"

    mock_dependencies["NuclearAndGasDataCollection"].return_value = MagicMock()

    mock_report_instance = MagicMock()
    mock_dependencies["NuclearAndGasReportGenerator"].return_value.generate_report.return_value = mock_report_instance

    mock_response = MagicMock()
    mock_response.qa_report_id = data_id

    api_client = mock_dependencies["config"].dataland_client.eu_taxonomy_nuclear_gas_qa_api
    api_client.post_nuclear_and_gas_data_qa_report.return_value = mock_response

    result = old_review_dataset(data_id)

    assert result == data_id


def test_review_dataset_dataset_not_found(mock_dependencies: MagicMock) -> None:
    """Test reviewing a dataset that does not exist raises DatasetNotFoundError."""
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = None

    with pytest.raises(DatasetNotFoundError):
        old_review_dataset("missing_id")


def test_review_dataset_returns_existing_report(mock_dependencies: MagicMock) -> None:
    """Test reviewing a dataset returns existing report if already reviewed."""
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = MagicMock()
    mock_dependencies["get_entity"].return_value = SimpleNamespace(report_id="EXISTING")

    result = old_review_dataset("id123")

    assert result == "EXISTING"


def test_review_dataset_force_review_deletes_old(mock_dependencies: MagicMock) -> None:
    """Test that force_review deletes old report and creates a new one."""
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = MagicMock(data="d")
    mock_dependencies["get_entity"].return_value = SimpleNamespace(report_id="OLD")

    mock_dependencies["NuclearAndGasDataCollection"].return_value = MagicMock()

    mock_response = MagicMock()
    mock_response.qa_report_id = "NEW"

    mock_dependencies[
        "config"
    ].dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report.return_value = mock_response

    result = old_review_dataset("id123", force_review=True)

    mock_dependencies["delete_entity"].assert_called_once()
    assert result == "NEW"


def test_review_dataset_data_collection_error(mock_dependencies: MagicMock) -> None:
    """Test that DataCollectionError is raised when data collection fails."""
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = MagicMock()
    mock_dependencies["get_entity"].return_value = None
    mock_dependencies["NuclearAndGasDataCollection"].side_effect = RuntimeError("boom")

    with pytest.raises(DataCollectionError):
        old_review_dataset("id123")


def test_review_dataset_ocr_failure(mock_dependencies: MagicMock) -> None:
    """Test that OCRProcessingError is raised when OCR processing fails."""
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = MagicMock(data="d")
    mock_dependencies["get_entity"].return_value = None
    mock_dependencies["NuclearAndGasDataCollection"].return_value = MagicMock()

    mock_dependencies["pages_provider"].get_relevant_page_numbers.return_value = [1]
    mock_dependencies["pages_provider"].get_relevant_pages_of_pdf.return_value = MagicMock()

    mock_dependencies["text_to_doc_intelligence"].old_get_markdown_from_dataset.side_effect = Exception("ocr fail")

    with pytest.raises(OCRProcessingError):
        old_review_dataset("id123")


def test_review_dataset_submission_error(mock_dependencies: MagicMock) -> None:
    """Test that ReportSubmissionError is raised when report submission fails."""
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = MagicMock(data="d")
    mock_dependencies["get_entity"].return_value = None
    mock_dependencies["NuclearAndGasDataCollection"].return_value = MagicMock()

    mock_dependencies["pages_provider"].get_relevant_pages_of_pdf.return_value = None

    mock_dependencies[
        "config"
    ].dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report.side_effect = Exception(
        "api down"
    )

    with pytest.raises(ReportSubmissionError):
        old_review_dataset("id123")


def test_review_dataset_use_ocr_false(mock_dependencies: MagicMock) -> None:
    """Test reviewing a dataset with use_ocr set to False."""
    mock_dependencies["dataset_provider"].get_dataset_by_id.return_value = MagicMock(data="d")
    mock_dependencies["get_entity"].return_value = None
    mock_dependencies["NuclearAndGasDataCollection"].return_value = MagicMock()

    mock_response = MagicMock()
    mock_response.qa_report_id = "NO_OCR"

    mock_dependencies[
        "config"
    ].dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report.return_value = mock_response

    result = old_review_dataset("id123", use_ocr=False)

    assert result == "NO_OCR"


@patch("dataland_qa_lab.review.dataset_reviewer.config")
def test_validate_datapoint_missing_datasource(mock_config: MagicMock) -> None:
    """Test validating a datapoint with missing dataSource raises ValueError."""
    dp = SimpleNamespace(
        data_point_type="type",
        data_point=json.dumps({"value": "X"}),
    )
    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp

    with pytest.raises(ValueError):  # noqa: PT011
        validate_datapoint("dp1", ai_model="gpt")


@patch("dataland_qa_lab.review.dataset_reviewer._get_file_using_ocr", return_value="CTX")
@patch(
    "dataland_qa_lab.review.dataset_reviewer.ai.execute_prompt",
    new_callable=MagicMock,
)
@patch("dataland_qa_lab.review.dataset_reviewer.config")
def test_validate_datapoint_accepted(
    mock_config: MagicMock,
    mock_ai: MagicMock,
    mock_ocr: MagicMock,  # noqa: ARG001
) -> None:
    """Test validating a datapoint that is accepted."""
    dp = fake_dp("dp1", value="YES")
    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp

    mock_ai.return_value = {
        "answer": "YES",
        "confidence": 0.9,
        "reasoning": "matched",
    }

    validation_prompts["extendedDecimalEstimatedScope1GhgEmissionsInTonnes"] = {
        "prompt": "{context}",
    }

    result = validate_datapoint("dp1", ai_model="gpt")

    assert result.qa_status == QaStatus.ACCEPTED
    assert result.confidence == 0.9
    assert result.reasoning == "matched"


@patch("dataland_qa_lab.review.dataset_reviewer._get_file_using_ocr", return_value="CTX")
@patch(
    "dataland_qa_lab.review.dataset_reviewer.ai.execute_prompt",
    new_callable=MagicMock,
)
@patch("dataland_qa_lab.review.dataset_reviewer.config")
def test_validate_datapoint_override(
    mock_config: MagicMock,
    mock_ai: MagicMock,
    mock_ocr: MagicMock,  # noqa: ARG001
) -> None:
    """Test validating a datapoint with override updates Dataland QA status."""
    dp = fake_dp("dp1", value="A")
    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp

    mock_ai.return_value = {
        "answer": "B",
        "confidence": 0.1,
        "reasoning": "different",
    }

    validation_prompts["extendedDecimalEstimatedScope1GhgEmissionsInTonnes"] = {
        "prompt": "{context}",
    }

    validate_datapoint("dp1", ai_model="gpt", override=True)

    mock_config.dataland_client.qa_api.change_data_point_qa_status.assert_called_once()


@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.get_entity")
@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.add_entity")
@patch("dataland_qa_lab.review.dataset_reviewer.text_to_doc_intelligence.extract_pdf")
@patch("dataland_qa_lab.review.dataset_reviewer._get_document")
def test_get_file_using_ocr_uses_cache(
    mock_get_document: MagicMock,
    mock_extract_pdf: MagicMock,
    mock_add: MagicMock,
    mock_get: MagicMock,
) -> None:
    """Test that _get_file_using_ocr uses cached OCR output if available."""
    mock_get.return_value = SimpleNamespace(ocr_output="CACHED")

    out = _get_file_using_ocr("file.pdf", "ref", 1)

    assert out == "CACHED"
    mock_get_document.assert_not_called()
    mock_extract_pdf.assert_not_called()
    mock_add.assert_not_called()


@patch("dataland_qa_lab.review.dataset_reviewer.config")
@patch("dataland_qa_lab.review.dataset_reviewer.ai.execute_prompt")
@patch("dataland_qa_lab.review.dataset_reviewer._get_file_using_ocr")
def test_validate_ghg_intensity_scope1_accept(
    mock_ocr: MagicMock, 
    mock_ai: MagicMock,
    mock_config: MagicMock
) -> None:
    """Test ACCEPT case for GHG intensity scope 1 per million EUR revenue."""
    
    mock_ocr.return_value = """
    Sustainability Performance Metrics 2024
    The Scope 1 GHG emissions intensity for the reporting period was
    245.7 tonnes CO2e per million EUR revenue.
    """
    
    mock_ai.return_value = {
        "answer": "245.7",
        "confidence": 0.95,
        "reasoning": "Found Scope 1 GHG intensity value"
    }
    
    dp = fake_dp(
        "dp_ghg_intensity_scope1",
        dp_type="extendedDecimalGhgIntensityScope1InTonnesPerMillionEURRevenue",
        value="245.7"
    )
    
    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp
    mock_config.validation_prompts = {
        "extendedDecimalGhgIntensityScope1InTonnesPerMillionEURRevenue": {
            "prompt": "Extract: {context}"
        }
    }
    
    result = validate_datapoint("dp_ghg_intensity_scope1", ai_model="gpt-4o")
    
    assert result.qa_status == QaStatus.ACCEPTED
    assert result.predicted_answer == "245.7"
    assert result.data_point_type == "extendedDecimalGhgIntensityScope1InTonnesPerMillionEURRevenue"


@patch("dataland_qa_lab.review.dataset_reviewer.config")
@patch("dataland_qa_lab.review.dataset_reviewer.ai.execute_prompt")
@patch("dataland_qa_lab.review.dataset_reviewer._get_file_using_ocr")
def test_validate_ghg_intensity_scope1_reject(
    mock_ocr: MagicMock, 
    mock_ai: MagicMock, 
    mock_config: MagicMock
) -> None:
    """Test REJECT case for GHG intensity scope 1."""
    
    mock_ocr.return_value = "Scope 1 intensity: 245.7 tonnes per million EUR revenue."
    
    mock_ai.return_value = {
        "answer": "245.7",
        "confidence": 0.88,
        "reasoning": "Found value"
    }
    
    dp = fake_dp(
        "dp1_reject",
        dp_type="extendedDecimalGhgIntensityScope1InTonnesPerMillionEURRevenue",
        value="250.0"
    )
    
    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp
    mock_config.validation_prompts = {
        "extendedDecimalGhgIntensityScope1InTonnesPerMillionEURRevenue": {"prompt": "{context}"}
    }
    
    result = validate_datapoint("dp1_reject", ai_model="gpt-4o")
    
    assert result.qa_status == QaStatus.REJECTED
    assert result.predicted_answer == "245.7"
    assert result.previous_answer == "250.0"


@patch("dataland_qa_lab.review.dataset_reviewer.config")
@patch("dataland_qa_lab.review.dataset_reviewer.ai.execute_prompt")
@patch("dataland_qa_lab.review.dataset_reviewer._get_file_using_ocr")
def test_validate_ghg_intensity_scope2_accept(
    mock_ocr: MagicMock, 
    mock_ai: MagicMock, 
    mock_config: MagicMock
) -> None:
    """Test ACCEPT case for GHG intensity scope 2."""
    
    mock_ocr.return_value = "Scope 2 intensity: 128.4 tonnes CO2e per million EUR revenue."
    
    mock_ai.return_value = {"answer": "128.4", "confidence": 0.93, "reasoning": "Found value"}
    
    dp = fake_dp(
        "dp2_accept",
        dp_type="extendedDecimalGhgIntensityScope2InTonnesPerMillionEURRevenue",
        value="128.4"
    )
    
    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp
    mock_config.validation_prompts = {
        "extendedDecimalGhgIntensityScope2InTonnesPerMillionEURRevenue": {"prompt": "{context}"}
    }
    
    result = validate_datapoint("dp2_accept", ai_model="gpt-4o")
    
    assert result.qa_status == QaStatus.ACCEPTED
    assert result.predicted_answer == "128.4"


@patch("dataland_qa_lab.review.dataset_reviewer.config")
@patch("dataland_qa_lab.review.dataset_reviewer.ai.execute_prompt")
@patch("dataland_qa_lab.review.dataset_reviewer._get_file_using_ocr")
def test_validate_ghg_intensity_scope3_accept(
    mock_ocr: MagicMock, 
    mock_ai: MagicMock, 
    mock_config: MagicMock
) -> None:
    """Test ACCEPT case for GHG intensity scope 3."""
    
    mock_ocr.return_value = "Scope 3 intensity: 1847.2 tonnes CO2e per million EUR revenue."
    
    mock_ai.return_value = {"answer": "1847.2", "confidence": 0.90, "reasoning": "Found value"}
    
    dp = fake_dp(
        "dp3_accept",
        dp_type="extendedDecimalGhgIntensityScope3InTonnesPerMillionEURRevenue",
        value="1847.2"
    )
    
    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp
    mock_config.validation_prompts = {
        "extendedDecimalGhgIntensityScope3InTonnesPerMillionEURRevenue": {"prompt": "{context}"}
    }
    
    result = validate_datapoint("dp3_accept", ai_model="gpt-4o")
    
    assert result.qa_status == QaStatus.ACCEPTED
    assert result.predicted_answer == "1847.2"


@patch("dataland_qa_lab.review.dataset_reviewer.config")
@patch("dataland_qa_lab.review.dataset_reviewer.ai.execute_prompt")
@patch("dataland_qa_lab.review.dataset_reviewer._get_file_using_ocr")
def test_validate_ghg_intensity_scope4_accept(
    mock_ocr: MagicMock, 
    mock_ai: MagicMock, 
    mock_config: MagicMock
) -> None:
    """Test ACCEPT case for GHG intensity scope 4."""
    
    mock_ocr.return_value = "Scope 4 avoided emissions: 320.5 tonnes per million EUR revenue."
    
    mock_ai.return_value = {"answer": "320.5", "confidence": 0.89, "reasoning": "Found value"}
    
    dp = fake_dp(
        "dp4_accept",
        dp_type="extendedDecimalGhgIntensityScope4InTonnesPerMillionEURRevenue",
        value="320.5"
    )
    
    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp
    mock_config.validation_prompts = {
        "extendedDecimalGhgIntensityScope4InTonnesPerMillionEURRevenue": {"prompt": "{context}"}
    }
    
    result = validate_datapoint("dp4_accept", ai_model="gpt-4o")
    
    assert result.qa_status == QaStatus.ACCEPTED
    assert result.predicted_answer == "320.5"


@patch("dataland_qa_lab.review.dataset_reviewer.config")
@patch("dataland_qa_lab.review.dataset_reviewer.ai.execute_prompt")
@patch("dataland_qa_lab.review.dataset_reviewer._get_file_using_ocr")
def test_validate_financed_scope3_accept(
    mock_ocr: MagicMock, 
    mock_ai: MagicMock, 
    mock_config: MagicMock
) -> None:
    """Test ACCEPT case for financed Scope 3 emissions."""
    
    mock_ocr.return_value = "Financed Scope 3 emissions: 2547893.0 tonnes CO2e."
    
    mock_ai.return_value = {"answer": "2547893.0", "confidence": 0.94, "reasoning": "Found value"}
    
    dp = fake_dp(
        "dp_fin3_accept",
        dp_type="extendedDecimalFinancedScope3Emissions",
        value="2547893.0"
    )
    
    mock_config.dataland_client.data_points_api.get_data_point.return_value = dp
    mock_config.validation_prompts = {
        "extendedDecimalFinancedScope3Emissions": {"prompt": "{context}"}
    }
    
    result = validate_datapoint("dp_fin3_accept", ai_model="gpt-4o")
    
    assert result.qa_status == QaStatus.ACCEPTED
    assert result.predicted_answer == "2547893.0"

@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.get_entity", return_value=None)
@patch("dataland_qa_lab.review.dataset_reviewer.database_engine.add_entity")
@patch("dataland_qa_lab.review.dataset_reviewer.text_to_doc_intelligence.extract_pdf", return_value="NEW")
@patch("dataland_qa_lab.review.dataset_reviewer._get_document", return_value=b"PDF")
def test_get_file_using_ocr_generates_new_ocr(
    mock_get_document: MagicMock,  # noqa: ARG001
    mock_extract_pdf: MagicMock,  # noqa: ARG001
    mock_add: MagicMock,
    mock_get: MagicMock,  # noqa: ARG001
) -> None:
    """Test that _get_file_using_ocr generates new OCR output when not cached."""
    out = _get_file_using_ocr("file.pdf", "ref", 2)

    assert out == "NEW"
    mock_add.assert_called_once()
