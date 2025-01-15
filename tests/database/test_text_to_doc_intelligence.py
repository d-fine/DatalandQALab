from unittest.mock import MagicMock, patch

import pytest
from azure.ai.documentintelligence.models import AnalyzeResult
from sqlalchemy.exc import SQLAlchemyError

from dataland_qa_lab.pages.text_to_doc_intelligence import add_document_if_not_exists, extract_text_of_pdf


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.config.get_config")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.DocumentIntelligenceClient")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.AzureKeyCredential")
def test_extract_text_of_pdf(
    mock_credential: MagicMock,
    mock_client: MagicMock,
    mock_config: MagicMock) -> None:
    """Test to ensure that the text of a PDF is extracted correctly."""
    mock_pdf = MagicMock()
    mock_result = MagicMock(spec=AnalyzeResult)
    mock_poller = MagicMock()
    mock_poller.result.return_value = mock_result
    mock_client_instance = mock_client.return_value
    mock_client_instance.begin_analyze_document.return_value = mock_poller
    mock_config.return_value = MagicMock(azure_docintel_api_key="fake_key", azure_docintel_endpoint="fake_endpoint")

    result = extract_text_of_pdf(mock_pdf)

    mock_client.assert_called_once_with(endpoint="fake_endpoint", credential=mock_credential.return_value)
    mock_client_instance.begin_analyze_document.assert_called_once_with(
        "prebuilt-layout",
        analyze_request=mock_pdf,
        content_type="application/octet-stream",
        output_content_format="markdown"
    )
    assert result == mock_result


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.extract_text_of_pdf")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.database_engine")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.database_tables")
def test_add_document_if_not_exists_new_entry(
    mock_tables: MagicMock,
    mock_engine: MagicMock,
    mock_extract_text: MagicMock) -> None:
    """test to ensure adding a document works as intended."""
    mock_session = MagicMock()
    mock_engine.SessionLocal.return_value.__enter__.return_value = mock_session
    mock_engine.create_tables.return_value = None
    mock_extract_text.return_value = "mocked_text"
    mock_tables.ReviewedDatasetMarkdowns.return_value = None

    data_id = "test_id"
    relevant_pages_pdf_reader = "test_reader"

    result = add_document_if_not_exists(data_id, relevant_pages_pdf_reader)

    mock_engine.create_tables.assert_called_once()
    mock_session.query.return_value.filter_by.return_value.first.assert_called_once()
    mock_extract_text.assert_called_once_with(relevant_pages_pdf_reader)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    assert result == "mocked_text"


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.extract_text_of_pdf")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.database_engine")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.database_tables")
def test_add_document_if_not_exists_existing_entry(
    mock_engine: MagicMock,
    mock_extract_text: MagicMock) -> None:
    """test to ensure updating a document works as intended."""
    mock_session = MagicMock()
    mock_engine.SessionLocal.return_value.__enter__.return_value = mock_session
    mock_engine.create_tables.return_value = None
    mock_extract_text.return_value = "mocked_text"
    mock_existing_entry = MagicMock()
    mock_existing_entry.relevant_pages_pdf_reader = "old_reader"
    mock_existing_entry.markdown_text = "old_text"
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_existing_entry

    data_id = "test_id"
    relevant_pages_pdf_reader = "test_reader"

    result = add_document_if_not_exists(data_id, relevant_pages_pdf_reader)

    mock_engine.create_tables.assert_called_once()
    mock_session.query.return_value.filter_by.return_value.first.assert_called_once()
    mock_extract_text.assert_called_once_with(relevant_pages_pdf_reader)
    mock_session.commit.assert_called_once()
    assert result == "mocked_text"


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.database_engine")
def test_add_document_if_not_exists_sqlalchemy_error(mock_engine: MagicMock) -> None:
    """Test to ensure that an SQLAlchemyError is caught."""
    mock_session = MagicMock()
    mock_engine.SessionLocal.return_value.__enter__.return_value = mock_session
    mock_engine.create_tables.return_value = None
    mock_session.commit.side_effect = SQLAlchemyError

    data_id = "test_id"
    relevant_pages_pdf_reader = "test_reader"

    with pytest.raises(SQLAlchemyError):
        add_document_if_not_exists(data_id, relevant_pages_pdf_reader)

    mock_engine.create_tables.assert_called_once()
    mock_session.query.return_value.filter_by.return_value.first.assert_called_once()
    mock_session.commit.assert_called_once()
