import io

import pytest
from pypdf import PdfReader, PdfWriter

from dataland_qa_lab.dataland import data_extraction


@pytest.fixture
def mock_pdf_with_pages() -> PdfReader:
    pdf_writer = PdfWriter()
    for _i in range(1, 4):
        pdf_writer.add_blank_page(width=200, height=200)
    pdf_stream = io.BytesIO()
    pdf_writer.write(pdf_stream)
    pdf_stream.seek(0)
    return PdfReader(pdf_stream)


def test_get_relevant_page_of_pdf(mock_pdf_with_pages: PdfReader) -> None:
    page_number = 2
    full_pdf = mock_pdf_with_pages

    result_stream = data_extraction.get_relevant_page_of_pdf(page_number, full_pdf)

    assert isinstance(result_stream, io.BytesIO), "The result should be of type BytesIO"

    extracted_pdf = PdfReader(result_stream)
    assert len(extracted_pdf.pages) == 1, "The pdf should have only one page"
