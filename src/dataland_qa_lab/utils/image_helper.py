import io
import logging
import base64
from typing import Literal


from PIL import Image

from dataland_qa_lab.utils.config import get_config

logger = logging.getLogger(__name__)

ImageFormat = Literal["PNG", "JPEG", "WEBP"]

def encode_image_to_base64(image: Image.Image, image_format : ImageFormat | None = None, quality: int | None = None) -> str:
    """Encodes a PIL Image to a base64 string for API usage."""
    if image is None:
        raise ValueError("Cannot encode: Image is None.")
    
    config = get_config()
    
    if image_format is None:
        image_format = config.vision.image_format
    if quality is None:
        quality = config.vision.jpeg_quality
    
    if not (1 <= quality <= 100):
        raise ValueError(f"Quality must be between 1 and 100, got {quality}.")
    
    format_upper = image_format.upper()
    
    try: 
        if format_upper == "JPEG" and image.mode in ("RGBA", "P", "LA"):
            logger.debug("Converting image from %s to RGB with white background for JPEG encoding.", image.mode)
            
            if image.mode == "P":
                image = image.convert("RGBA")
            
            background = Image.new("RGB", image.size, (255, 255, 255))
            
            if image.mode in ("RGBA", "LA"):
                background.paste(image, mask = image.getchannel("A"))
            else: 
                background.paste(image)
            
            image = background
        
        with io.BytesIO() as buffer:
            save_kwargs = {"format": format_upper}
            
            if format_upper == "JPEG":
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True
            
            image.save(buffer, **save_kwargs)
            bytes_data = buffer.getvalue()
            
            base64_str = base64.b64encode(bytes_data).decode("utf-8")
            
            logger.debug("Successfully encoded image to base64 (%s, %d bytes, quality=%d)", format_upper, len(bytes_data), quality)
            
            return base64_str
        
    except OSError as e:
        logger.error("Failed to encode image to %s: %s", format_upper, str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error during image encoding: %s", str(e))
        raise RuntimeError("Image encoding failed.") from e
        