from unittest.mock import MagicMock, patch

import pypdf
from azure.ai.documentintelligence.models import AnalyzeResult

from dataland_qa_lab.pages.text_to_doc_intelligence import extract_text_of_pdf, get_markdown_from_dataset


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.config.get_config")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.DocumentIntelligenceClient")
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.AzureKeyCredential")
def test_extract_text_of_pdf(mock_credential: MagicMock, mock_client: MagicMock, mock_config: MagicMock) -> None:
    mock_pdf = MagicMock()
    mock_result = MagicMock(spec=AnalyzeResult)
    mock_result.content = "content"
    mock_poller = MagicMock()
    mock_poller.result.return_value = mock_result
    mock_client_instance = mock_client.return_value
    mock_client_instance.begin_analyze_document.return_value = mock_poller
    mock_config.return_value = MagicMock(azure_docintel_api_key="fake_key", azure_docintel_endpoint="fake_endpoint")

    result = extract_text_of_pdf(mock_pdf)

    mock_client.assert_called_once_with(endpoint="fake_endpoint", credential=mock_credential.return_value)
    mock_client_instance.begin_analyze_document.assert_called_once_with(
        "prebuilt-layout",
        body=mock_pdf,
        content_type="application/octet-stream",
        output_content_format="markdown",
    )
    assert result == "content"


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.extract_text_of_pdf")
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

    result = get_markdown_from_dataset(data_id=data_id, relevant_pages_pdf_reader=pdf_reader, page_numbers=pages)

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

    result = get_markdown_from_dataset(data_id=data_id, relevant_pages_pdf_reader=pdf_reader, page_numbers=pages)

    mock_get_entity.assert_called_once()
    mock_add_entity.assert_not_called()
    assert result == "old_text"
