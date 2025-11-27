from qa_lab.database.database_tables import CachedDocument


def test_cached_document_fields() -> None:
    """Test that CachedDocument initializes correctly."""
    doc = CachedDocument(file_name="test.pdf", file_reference="ref123", ocr_output="Some OCR text", page=1)

    assert doc.file_name == "test.pdf"
    assert doc.file_reference == "ref123"
    assert doc.ocr_output == "Some OCR text"
    assert doc.page == 1


def test_cached_document_id_is_none_by_default() -> None:
    """ID should be None until persisted to DB."""
    doc = CachedDocument(file_name="test.pdf", file_reference="ref123", ocr_output="Some OCR text", page=1)
    assert doc.id is None
