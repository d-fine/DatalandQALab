import io

import fitz
import pytest
from PIL import Image

from dataland_qa_lab.utils import pdf_handler


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Returns a simple PDF file in bytes."""
    doc = fitz.open()
    doc.new_page()
    doc.new_page()
    doc.new_page()
    return doc.tobytes()


def test_extract_single_page(sample_pdf_bytes: bytes) -> None:
    """Test extracting a single page from a PDF."""
    result_stream = pdf_handler.extract_single_page(sample_pdf_bytes, page_number=2)
    with fitz.open(stream=result_stream, filetype="pdf") as result_doc:
        assert len(result_doc) == 1


def test_extract_single_page_invalid_page(sample_pdf_bytes: bytes) -> None:
    """Test extracting a page number that exceeds total pages."""
    with pytest.raises(ValueError, match="exceeds total pages"):
        pdf_handler.extract_single_page(sample_pdf_bytes, page_number=5)


def test_render_pdf_to_image(sample_pdf_bytes: bytes) -> None:
    """Test rendering PDF pages to images."""
    pdf_stream = io.BytesIO(sample_pdf_bytes)
    images = pdf_handler.render_pdf_to_image(pdf_stream, dpi=72)
    assert len(images) == 3
    assert isinstance(images[0], Image.Image)
    assert images[0].width > 0
    assert images[0].height > 0


def test_render_pdf_to_image_empty_stream() -> None:
    """Test rendering with an empty PDF stream."""
    pdf_stream = io.BytesIO(b"")
    with pytest.raises(ValueError, match="PDF stream is empty"):
        pdf_handler.render_pdf_to_image(pdf_stream, dpi=72)


def test_render_pdf_to_image_corrupt_pdf() -> None:
    """Test rendering with a corrupt PDF stream."""
    pdf_stream = io.BytesIO(b"%PDF-1.4\n%CorruptContent")
    with pytest.raises(RuntimeError) as excinfo:
        pdf_handler.render_pdf_to_image(pdf_stream, dpi=72)
    assert "Failed to render PDF to images" in str(excinfo.value)


def test_extract_single_page_zero_or_negative(sample_pdf_bytes: bytes) -> None:
    """Test extracting an invalid lower bound page number (0 or negative)."""

    with pytest.raises(ValueError):  # noqa: PT011
        pdf_handler.extract_single_page(sample_pdf_bytes, page_number=0)

    with pytest.raises(ValueError):  # noqa: PT011
        pdf_handler.extract_single_page(sample_pdf_bytes, page_number=-1)


def test_extract_single_page_none_input() -> None:
    """Test behavior when input is None."""

    with pytest.raises((ValueError, AttributeError, TypeError)):
        pdf_handler.extract_single_page(None, page_number=1)
