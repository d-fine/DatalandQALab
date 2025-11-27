from unittest.mock import ANY, MagicMock, patch

from qa_lab.validator.ocr import extract_pdf

dummy_pdf = b"%PDF-1.4 dummy content"

mock_config = MagicMock()
mock_config.azure_docintel_api_key = "fake-key"
mock_config.azure_docintel_endpoint = "https://fake-endpoint/"


@patch("qa_lab.validator.ocr.DocumentIntelligenceClient")
@patch("qa_lab.validator.ocr.config", new=mock_config)
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


@patch("qa_lab.validator.ocr.DocumentIntelligenceClient")
@patch("qa_lab.validator.ocr.config", new=mock_config)
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


@patch("qa_lab.validator.ocr.AzureKeyCredential")
@patch("qa_lab.validator.ocr.DocumentIntelligenceClient")
@patch("qa_lab.validator.ocr.config", new=mock_config)
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
