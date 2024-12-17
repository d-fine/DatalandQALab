import io

import pytest
from pypdf import PdfReader, PdfWriter

from dataland_qa_lab.dataland import data_extraction


@pytest.fixture
def mock_pdf_with_pages() -> PdfReader:
    """Erstellt eine PDF-Datei mit mehreren Seiten zum Testen."""
    pdf_writer = PdfWriter()
    # Erstelle Seiten mit Testinhalten
    for _i in range(1, 4):  # Eine 3-seitige PDF
        pdf_writer.add_blank_page(width=200, height=200)

    # Schreibe die PDF in einen BytesIO-Stream
    pdf_stream = io.BytesIO()
    pdf_writer.write(pdf_stream)
    pdf_stream.seek(0)  # Setze den Zeiger auf den Anfang des Streams

    return PdfReader(pdf_stream)


def test_get_relevant_page_of_pdf(mock_pdf_with_pages: PdfReader) -> None:
    """Testet die Extraktion einer Seite aus einer PDF-Datei."""
    # Arrange
    page_number = 2  # Die 2. Seite extrahieren
    full_pdf = mock_pdf_with_pages

    # Act
    result_stream = data_extraction.get_relevant_page_of_pdf(page_number, full_pdf)

    # Assert
    # Prüfen, ob das Ergebnis ein BytesIO-Objekt ist
    assert isinstance(result_stream, io.BytesIO), "Das Ergebnis sollte ein BytesIO-Objekt sein."

    # Prüfen, ob die extrahierte Seite gültig ist
    extracted_pdf = PdfReader(result_stream)
    assert len(extracted_pdf.pages) == 1, "Die extrahierte PDF sollte genau eine Seite enthalten."
