import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dataland_qa_lab.data_point_flow import ocr


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.ocr.database_engine")
@patch("dataland_qa_lab.data_point_flow.ocr.extract_pdf")
async def test_run_ocr_on_document_new_document(mock_extract_pdf: MagicMock, mock_db_engine: MagicMock):
    """Test OCR on a new document (not cached)."""
    # Mock the database to return no cached document
    mock_db_engine.get_entity.return_value = None
    # Mock extract_pdf to return "mocked OCR output"
    mock_extract_pdf.return_value = "mocked OCR output"

    fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")
    result = await ocr.run_ocr_on_document("file.pdf", "ref123", 1, fake_pdf)

    # Should return mocked OCR output
    assert result == "mocked OCR output"
    # Should call extract_pdf once
    mock_extract_pdf.assert_called_once_with(fake_pdf)
    # Should save to database
    mock_db_engine.add_entity.assert_called_once()
    added_entity = mock_db_engine.add_entity.call_args[0][0]
    assert added_entity.file_name == "file.pdf"
    assert added_entity.file_reference == "ref123"
    assert added_entity.ocr_output == "mocked OCR output"
    assert added_entity.page == 1


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.ocr.database_engine")
@patch("dataland_qa_lab.data_point_flow.ocr.extract_pdf")
async def test_run_ocr_on_document_cached_document(mock_extract_pdf: MagicMock, mock_db_engine: MagicMock):
    """Test OCR on a cached document."""
    # Mock the database to return a cached document
    cached_entity = MagicMock()
    cached_entity.ocr_output = "cached OCR text"
    mock_db_engine.get_entity.return_value = cached_entity

    fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")
    result = await ocr.run_ocr_on_document("file.pdf", "ref123", 1, fake_pdf)

    # Should return cached text
    assert result == "cached OCR text"
    # Should NOT call extract_pdf since it's cached
    mock_extract_pdf.assert_not_called()
    # Should NOT call add_entity
    mock_db_engine.add_entity.assert_not_called()
