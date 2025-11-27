import json
from unittest.mock import MagicMock, patch

import pytest

from qa_lab.utils.prompts import get_prompts


def test_get_prompts_success() -> None:
    """Test that get_prompts correctly reads and combines JSON files."""
    mock_json_content1 = json.dumps({"type1": {"prompt": "prompt1"}})
    mock_json_content2 = json.dumps({"type2": {"prompt": "prompt2"}})

    # Mock Path.glob to return two fake files
    mock_file1 = MagicMock()
    mock_file1.read_text.return_value = mock_json_content1
    mock_file2 = MagicMock()
    mock_file2.read_text.return_value = mock_json_content2

    with (
        patch("qa_lab.utils.prompts.Path.exists", return_value=True),
        patch("qa_lab.utils.prompts.Path.glob", return_value=[mock_file1, mock_file2]),
    ):
        prompts = get_prompts()

    assert prompts == {
        "type1": {"prompt": "prompt1"},
        "type2": {"prompt": "prompt2"},
    }
    mock_file1.read_text.assert_called_once()
    mock_file2.read_text.assert_called_once()


def test_get_prompts_directory_missing() -> None:
    """Test that FileNotFoundError is raised when prompts directory is missing."""
    with patch("qa_lab.utils.prompts.Path.exists", return_value=False), pytest.raises(FileNotFoundError):
        get_prompts()


def test_get_prompts_invalid_json_raises_error() -> None:
    """Test that invalid JSON raises JSONDecodeError."""
    mock_file = MagicMock()
    mock_file.read_text.return_value = "{ invalid json "

    with (
        patch("qa_lab.utils.prompts.Path.exists", return_value=True),
        patch("qa_lab.utils.prompts.Path.glob", return_value=[mock_file]),
        pytest.raises(json.JSONDecodeError),
    ):
        get_prompts()
