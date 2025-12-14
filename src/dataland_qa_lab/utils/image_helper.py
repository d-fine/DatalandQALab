import base64
import io
import logging
from typing import Literal

from PIL import Image

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)

ImageFormat = Literal["JPEG", "PNG", "WEBP"]


def encode_image_to_base64(image: Image.Image, image_format: ImageFormat | None = None) -> str:
    """Encode a PIL Image to a base64 string for Vision API."""
    if image is None:
        msg = "Image cannot be None."
        raise ValueError(msg)

    conf = config.get_config()
    if image_format is None:
        image_format = conf.vision.image_format

    format_upper = image_format.upper()

    try:
        if format_upper == "JPEG" and image.mode in {"RGBA", "P", "LA"}:
            logger.debug("Converting image from %s to RGB with white background for JPEG", image.mode)

            if image.mode == "P":
                image = image.convert("RGBA")

            background = Image.new("RGB", image.size, (255, 255, 255))

            if image.mode in {"RGBA", "LA"}:
                background.paste(image, mask=image.getchannel("A"))
            else:
                background.paste(image)
            image = background

        with io.BytesIO() as buffer:
            save_kwargs = {"format": format_upper}
            if format_upper == "JPEG":
                save_kwargs["quality"] = conf.vision.jpeg_quality
                save_kwargs["optimize"] = True
            image.save(buffer, **save_kwargs)
            byte_data = buffer.getvalue()
        base64_str = base64.b64encode(byte_data).decode("utf-8")
        logger.debug("Successfully encoded image to base64 with format %s.", format_upper)
        return base64_str  # noqa: TRY300

    except OSError as e:
        logger.exception("Error encoding image to base64.")
        msg = f"Failed to encode image to base64: {e}"
        raise RuntimeError(msg) from e
    except Exception as e:
        logger.exception("Unexpected error encoding image to base64.")
        msg = f"Unexpected error encoding image to base64: {e}"
        raise RuntimeError(msg) from e
