import json
import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from monitor.utils import load_config, store_output


@pytest.fixture
def test_env() -> Iterator[None]:
    """Provide temporary environment variables for testing."""
    prior_env = os.environ.copy()

    os.environ["QA_LAB_URL"] = "https://test.com"
    os.environ["DOCUMENTS"] = "test,test2"
    os.environ["AI_MODEL"] = "ai-model"
    os.environ["USE_OCR"] = "false"

    yield

    os.environ.clear()
    os.environ.update(prior_env)


@pytest.fixture
def empty_env() -> Iterator[None]:
    """Clear environment variables to do testing."""
    prior_env = os.environ.copy()
    os.environ.clear()

    yield

    os.environ.update(prior_env)


@pytest.fixture
def config_file() -> Iterator[Path]:
    """Create a temporary config file for testing."""
    config_content = {
        "qa_lab_url": "https://config.com",
        "documents": ["config1", "config2"],
        "ai_model": "config-model",
        "use_ocr": True,
    }

    config_path = Path(__file__).parent.parent.parent / "monitor" / "config.json"

    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config_content, f)

    yield config_path

    config_path.unlink()


def test_load_config(test_env: Iterator[None]) -> None:  # noqa: ARG001
    """Test loading configuration from environment variables."""

    values = load_config()

    assert values.qa_lab_url == "https://test.com"
    assert values.documents == ["test", "test2"]
    assert values.ai_model == "ai-model"
    assert values.use_ocr is False


def test_load_config_with_no_env_vars(
    empty_env: Iterator[None],  # noqa: ARG001
    config_file: Iterator[Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test loading configuration when no environment variables are set and a config file is used instead."""

    monkeypatch.setattr("monitor.utils.config_path", config_file)

    values = load_config()
    assert values.qa_lab_url == "https://config.com"
    assert values.documents == ["config1", "config2"]
    assert values.ai_model == "config-model"
    assert values.use_ocr is True


def test_store_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test storing output to a file."""

    data = {"key": "value"}
    file_name = "test_output"

    monkeypatch.setattr("monitor.utils.output_dir", tmp_path)

    store_output(data, file_name, format_as_json=True)

    files = list(tmp_path.glob(f"{file_name}-*"))
    assert len(files) == 1, "Output file was not created correctly"

    with files[0].open("r", encoding="utf-8") as f:
        content = json.load(f)
        assert content == data, "Contents do not match expected data"
