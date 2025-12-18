from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from dataland_qa_lab.utils import image_helper


def test_encode_image_none_error() -> None:
    """Test that passing None raises a ValueError."""
    with pytest.raises(ValueError, match="Image cannot be None"):
        _ = image_helper.encode_image_to_base64(None)


def test_encode_image_default_format() -> None:
    """Test encoding using the format from config."""
    image = Image.new("RGB", (10, 10), color="red")
    result = image_helper.encode_image_to_base64(image)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encode_image_jpeg_transparency_handling() -> None:
    """Test that RGBA images are converted correctly for JPEG encoding."""
    image = MagicMock(spec=Image.Image)
    image.mode = "RGBA"
    image.size = (100, 100)

    with patch("dataland_qa_lab.utils.image_helper.Image.new") as mock_new:
        mock_background = MagicMock()
        mock_new.return_value = mock_background
        image_helper.encode_image_to_base64(image, image_format="JPEG")
        mock_new.assert_called_with("RGB", image.size, (255, 255, 255))
        mock_background.paste.assert_called()


@patch("dataland_qa_lab.utils.image_helper.logger")
def test_encode_image_oserror_handling(mock_logger: MagicMock) -> None:
    """Test handling of OSError during save."""
    image = MagicMock(spec=Image.Image)
    image.mode = "RGB"
    image.save.side_effect = OSError("Save failed")
    with pytest.raises(RuntimeError) as excinfo:
        image_helper.encode_image_to_base64(image, image_format="PNG")

    assert "Failed to encode image to base64" in str(excinfo.value)
    mock_logger.exception.assert_called()


@patch("dataland_qa_lab.utils.image_helper.logger")
def test_encode_image_generic_error(mock_logger: MagicMock) -> None:
    """Test handling of unexpected exceptions."""
    image = MagicMock(spec=Image.Image)
    image.save.side_effect = Exception("Unexpected error")
    with pytest.raises(RuntimeError) as excinfo:
        image_helper.encode_image_to_base64(image)
    assert "Unexpected error encoding image to base64" in str(excinfo.value)
    mock_logger.exception.assert_called()
