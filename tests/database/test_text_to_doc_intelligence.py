from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, patch

import pypdf
from azure.ai.documentintelligence.models import AnalyzeResult

from dataland_qa_lab.pages.text_to_doc_intelligence import (
    extract_pdf,
    old_extract_text_of_pdf,
    old_get_markdown_from_dataset,
)

dummy_pdf = b"%PDF-1.4 dummy content"

mock_config = MagicMock()
mock_config.azure_docintel_api_key = "fake_key"
mock_config.azure_docintel_endpoint = "fake_endpoint"


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.config", new=mock_config)
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.DocumentIntelligenceClient")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.AzureKeyCredential")
def test_extract_text_of_pdf(mock_credential: MagicMock, mock_client: MagicMock) -> None:
    mock_pdf = MagicMock()
    mock_result = MagicMock(spec=AnalyzeResult)
    mock_result.content = "content"
    mock_poller = MagicMock()
    mock_poller.result.return_value = mock_result
    mock_client_instance = mock_client.return_value
    mock_client_instance.begin_analyze_document.return_value = mock_poller
    mock_config.return_value = MagicMock(azure_docintel_api_key="fake_key", azure_docintel_endpoint="fake_endpoint")

    result = old_extract_text_of_pdf(mock_pdf)

    mock_client.assert_called_once_with(endpoint="fake_endpoint", credential=mock_credential.return_value)
    mock_client_instance.begin_analyze_document.assert_called_once_with(
        "prebuilt-layout",
        body=mock_pdf,
        content_type="application/octet-stream",
        output_content_format="markdown",
    )
    assert result == "content"


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.old_extract_text_of_pdf")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.add_entity")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.get_entity")
def test_get_markdown_from_dataset_new_entry(
    mock_get_entity: MagicMock,
    mock_add_entity: MagicMock,
    mock_extract_text: MagicMock,
) -> None:
    mock_extract_text.return_value = "mocked_text"
    mock_get_entity.return_value = None

    data_id = "test_id"
    pdf_reader = MagicMock(spec=pypdf.PdfReader)
    pages = [1, 2, 3]

    result = old_get_markdown_from_dataset(data_id=data_id, relevant_pages_pdf_reader=pdf_reader, page_numbers=pages)

    mock_get_entity.assert_called_once()
    mock_extract_text.assert_called_once_with(pdf_reader)
    mock_add_entity.assert_called_once()
    assert result == "mocked_text"


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.add_entity")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.get_entity")
def test_get_markdown_from_dataset_existing_entry(
    mock_get_entity: MagicMock,
    mock_add_entity: MagicMock,
) -> None:
    mock_existing_entry = MagicMock()
    mock_existing_entry.pages = [1, 2]
    mock_existing_entry.markdown_text = "old_text"

    mock_get_entity.return_value = mock_existing_entry

    data_id = "test_id"
    pdf_reader = MagicMock(spec=pypdf.PdfReader)
    pages = [1, 2, 3]

    result = old_get_markdown_from_dataset(data_id=data_id, relevant_pages_pdf_reader=pdf_reader, page_numbers=pages)

    mock_get_entity.assert_called_once()
    mock_add_entity.assert_not_called()
    assert result == "old_text"


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.old_extract_text_of_pdf")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.get_german_time_as_string")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.add_entity")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.get_entity")
def test_get_markdown_from_dataset_saves_llm_version(
    mock_get_entity: MagicMock,
    mock_add_entity: MagicMock,
    mock_get_time: MagicMock,
    mock_extract_text: MagicMock,
) -> None:
    mock_get_entity.return_value = None

    mock_extract_text.return_value = "mocked_text"

    mock_get_time.return_value = "2025-12-12 12:34:56"

    data_id = "test_id"
    pdf_reader = MagicMock(spec=pypdf.PdfReader)
    pages = [1, 2, 3]
    llm_version = "gpt_4o"

    result = old_get_markdown_from_dataset(
        data_id=data_id,
        relevant_pages_pdf_reader=pdf_reader,
        page_numbers=pages,
        llm_version=llm_version,
    )

    assert result == "mocked_text"

    mock_add_entity.assert_called_once()
    saved_row = mock_add_entity.call_args[0][0]

    assert saved_row.data_id == data_id
    assert saved_row.llm_version == llm_version
    assert saved_row.markdown_text == "mocked_text"
    assert saved_row.page_numbers == pages
    assert saved_row.last_saved == "2025-12-12 12:34:56"
    assert saved_row.last_updated == "2025-12-12 12:34:56"


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.get_entity")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.get_german_time_as_string")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.add_entity")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.old_extract_text_of_pdf")
def test_get_markdown_from_dataset_updates_existing_llm_version(
    mock_extract_text: MagicMock,
    mock_add_entity: MagicMock,
    mock_get_time: MagicMock,
    mock_get_entity: MagicMock,
) -> None:
    """Test that existing markdown entries get updated with new pages, timestamps and llm_version."""
    mock_get_time.return_value = "2025-12-12 12:34:56"

    existing = SimpleNamespace(
        data_id="test_id",
        markdown_text="cached_text",
        page_numbers=[1, 2],
        last_saved="old",
        last_updated="old",
        llm_version="old-model",
    )
    mock_get_entity.return_value = existing

    data_id = "test_id"
    pdf_reader = MagicMock(spec=pypdf.PdfReader)
    pages = [3, 4]
    llm_version = "gpt-4o"

    result = old_get_markdown_from_dataset(
        data_id=data_id,
        relevant_pages_pdf_reader=pdf_reader,
        page_numbers=pages,
        llm_version=llm_version,
    )

    assert result == "cached_text"
    mock_extract_text.assert_not_called()
    mock_add_entity.assert_not_called()

    assert existing.page_numbers == pages
    assert existing.last_saved == "old"
    assert existing.last_updated == "2025-12-12 12:34:56"
    assert existing.llm_version == "gpt-4o"


# for the new method
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.DocumentIntelligenceClient")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.config", new=mock_config)
def test_extract_pdf_calls_client(mock_docintel_client_class: MagicMock) -> None:
    """Test that extract_pdf calls DocumentIntelligenceClient with correct parameters."""
    mock_client = MagicMock()
    mock_docintel_client_class.return_value = mock_client

    mock_poller = MagicMock()
    mock_client.begin_analyze_document.return_value = mock_poller

    mock_result = MagicMock()
    mock_result.content = "Extracted text"
    mock_poller.result.return_value = mock_result

    result = extract_pdf(dummy_pdf)

    mock_docintel_client_class.assert_called_once_with(endpoint=mock_config.azure_docintel_endpoint, credential=ANY)
    mock_client.begin_analyze_document.assert_called_once_with(
        "prebuilt-layout",
        body=dummy_pdf,
        content_type="application/octet-stream",
        output_content_format=mock_docintel_client_class.return_value.begin_analyze_document.call_args[1][
            "output_content_format"
        ],
    )
    assert result == "Extracted text"


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.DocumentIntelligenceClient")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.config", new=mock_config)
def test_extract_pdf_returns_content(mock_docintel_client_class: MagicMock) -> None:
    """Test that extract_pdf returns the correct content from the OCR process."""
    mock_client = MagicMock()
    mock_docintel_client_class.return_value = mock_client

    mock_poller = MagicMock()
    mock_client.begin_analyze_document.return_value = mock_poller

    expected_content = "This is a test document."
    mock_result = MagicMock()
    mock_result.content = expected_content
    mock_poller.result.return_value = mock_result

    result = extract_pdf(dummy_pdf)
    assert result == expected_content


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.AzureKeyCredential")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.DocumentIntelligenceClient")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.config", new=mock_config)
def test_extract_pdf_uses_credential(mock_docintel_client_class: MagicMock, mock_azure_key_cred: MagicMock) -> None:
    """Test that extract_pdf uses AzureKeyCredential with the correct API key."""
    mock_client = MagicMock()
    mock_docintel_client_class.return_value = mock_client
    mock_poller = MagicMock()
    mock_client.begin_analyze_document.return_value = mock_poller
    mock_result = MagicMock()
    mock_result.content = "text"
    mock_poller.result.return_value = mock_result

    extract_pdf(dummy_pdf)

    mock_azure_key_cred.assert_called_once_with(mock_config.azure_docintel_api_key)
