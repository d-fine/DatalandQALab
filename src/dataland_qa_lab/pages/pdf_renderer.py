import io
import logging

import fitz
from PIL import Image

from dataland_qa_lab.utils.config import get_config

logger = logging.getLogger(__name__)


def render_pdf_stream_to_images(pdf_stream: io.BytesIO, dpi: int | None = None) -> list[Image.Image]:
    """Renders each page of a PDF stream to a list of PIL Images."""
    if pdf_stream is None:
        msg = "PDF stream cannot be None."
        raise ValueError(msg)

    if dpi is None: 
        dpi = get_config().vision.dpi

    if dpi <= 0:
        msg = f"DPI must be a positive integer, got {dpi}."
        raise ValueError(msg)

    images: list[Image.Image] = []
    
    try:
        pdf_stream.seek(0)
        stream_content = pdf_stream.read()

        if not stream_content:
            msg = "PDF stream is empty."
            raise ValueError(msg)

        with fitz.open(stream=stream_content, filetype="pdf") as doc:
            if doc.page_count == 0:
                msg = "PDF document contains no pages."
                raise ValueError(msg)

            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)

            for page in doc:
                pix = page.get_pixmap(matrix=mat)
                
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                images.append(img)

        logger.info("Successfully rendered PDF to %d images at %d DPI.", len(images), dpi)
        return images

    except Exception as e:
        logger.error("Critical error rendering PDF to images: %s", e, exc_info=True)
        raise RuntimeError(f"Failed to render PDF to images: {e}") from e
        