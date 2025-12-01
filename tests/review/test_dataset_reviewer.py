import json
from collections.abc import Generator
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from src.dataland_qa_lab.review.dataset_reviewer import old_review_dataset, old_review_dataset_via_api


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

    result = old_review_dataset(data_id)

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
    )


@dataclass
class ExistingReport:
    report: str
    report_id: str


def test_review_dataset_returns_existing_report(mock_dependencies: dict[str, MagicMock]) -> None:
    """Test returning existing report without creating a new one."""
    data_id = "existing123"

    existing_report = ExistingReport(report="already exists", report_id="report_existing")

    mock_dependencies["get_entity"].return_value = existing_report

    result = old_review_dataset(data_id)

    assert result == existing_report.report_id
    mock_dependencies["add_entity"].assert_not_called()


@pytest.mark.parametrize(
    ("report_id", "expected"),
    [
        ("some_report_id", {"mock": "data"}),
        (None, {"error": "Failed to retrieve data"}),
    ],
)
def test_review_dataset_via_api(report_id: str, expected: dict) -> None:
    data_id = "test-data-id"

    with patch("src.dataland_qa_lab.review.dataset_reviewer.review_dataset", return_value=report_id):
        mock_report = MagicMock()
        mock_report.to_json.return_value = json.dumps({"mock": "data"})

        mock_client = MagicMock()
        mock_client.eu_taxonomy_nuclear_gas_qa_api.get_nuclear_and_gas_data_qa_report.return_value = mock_report

        mock_config = MagicMock()
        mock_config.dataland_client = mock_client

        with patch("src.dataland_qa_lab.review.dataset_reviewer.config.get_config", return_value=mock_config):
            result = old_review_dataset_via_api(data_id)

            assert result == expected
