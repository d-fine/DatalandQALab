import io
import logging

import fitz
from PIL import Image

logger = logging.getLogger(__name__)


def _raise_value_error(message: str) -> None:
    """Helper function to raise ValueError with a given message."""
    raise ValueError(message)


def _raise_runtime_error(message: str) -> None:
    """Helper function to raise RuntimeError with a given message."""
    raise RuntimeError(message)


def extract_single_page(full_pdf_bytes: bytes, page_number: int) -> io.BytesIO:
    """Extracts a single page from a PDF and returns it as a BytesIO stream."""
    if not full_pdf_bytes:
        msg = "Full PDF bytes cannot be empty."
        raise ValueError(msg)
    if page_number < 1:
        msg = f"Page number must be a positive integer, got {page_number}."
        raise ValueError(msg)

    try:
        with fitz.open(stream=full_pdf_bytes, filetype="pdf") as doc:
            if page_number > len(doc):
                msg = f"Page number {page_number} exceeds total pages {len(doc)}."
                raise ValueError(msg)  # noqa: TRY301

            page_index = page_number - 1
            page = doc.load_page(page_index)

            output_doc = fitz.open()
            new_page = output_doc.new_page(
                width=page.rect.width,
                height=page.rect.height,
            )

            new_page.show_pdf_page(new_page.rect, doc, page_index)

            output_stream = io.BytesIO(output_doc.tobytes())
            output_stream.seek(0)

            output_doc.close()
            logger.info("Successfully extracted page %d from PDF.", page_number)
            return output_stream

    except ValueError:
        raise
    except Exception as e:
        logger.exception("Error extracting page %d from PDF.", page_number)
        msg = f"Failed to extract page {page_number} from PDF: {e}"
        raise RuntimeError(msg) from e


def render_pdf_to_image(pdf_stream: io.BytesIO, dpi: int = 300) -> list[Image.Image]:
    """Render PDF pages to PIL Images."""
    if pdf_stream is None:
        msg = "PDF stream cannot be None."
        raise ValueError(msg)

    if dpi <= 0:
        msg = f"DPI must be a positive integer, got {dpi}."
        raise ValueError(msg)

    images: list[Image.Image] = []
    try:
        pdf_stream.seek(0)
        stream_content = pdf_stream.read()
        if not stream_content:
            msg = "PDF stream is empty."
            _raise_value_error(msg)

        with fitz.open(stream=stream_content, filetype="pdf") as doc:
            if len(doc) == 0:
                msg = "PDF document contains no pages."
                _raise_value_error(msg)

            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)

            for page_number, page in enumerate(doc, start=1):
                try:
                    pix = page.get_pixmap(matrix=mat)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    images.append(img)
                    logger.debug("Rendered page %d/%d (%dx%d)", page_number, len(doc), img.width, img.height)
                except Exception:
                    logger.exception("Failed to render page %d", page_number)
                    continue
        if not images:
            msg = "Failed to render any images from the PDF document."
            _raise_runtime_error(msg)

        logger.info("Successfully rendered PDF to %d images at %d DPI.", len(images), dpi)

    except ValueError:
        raise
    except Exception as e:
        logger.exception("Critical error rendering PDF to images.")
        msg = f"Failed to render PDF to images: {e}"
        raise RuntimeError(msg) from e
    return images
