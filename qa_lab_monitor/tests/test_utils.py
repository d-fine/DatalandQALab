import json
from unittest.mock import MagicMock, mock_open, patch


from qa_lab_monitor import utils
from qa_lab_monitor.utils import MonitorConfig

# -------------------------------
# Tests for load_config()
# -------------------------------


def test_load_config_from_json(tmp_path) -> None:  # noqa: ANN001
    """Test loading config from a valid JSON file."""
    config_data = {
        "qa_lab_url": "http://example.com",
        "data_points": ["dp1", "dp2"],
        "ai_model": "gpt-4",
        "use_ocr": True,
        "force_review": False,
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))

    with patch("qa_lab_monitor.utils.config_path", config_file):
        cfg = utils.load_config()

    assert isinstance(cfg, MonitorConfig)
    assert cfg.qa_lab_url == "http://example.com"
    assert cfg.data_points == ["dp1", "dp2"]
    assert cfg.ai_model == "gpt-4"
    assert cfg.use_ocr is True
    assert cfg.force_review is False


def test_load_config_from_env(monkeypatch: MagicMock) -> None:
    """Test loading config from environment variables if JSON is missing."""
    monkeypatch.setenv("QA_LAB_URL", "http://env.com")
    monkeypatch.setenv("DATA_POINTS", "dp3,dp4")
    monkeypatch.setenv("AI_MODEL", "gpt-3.5")
    monkeypatch.setenv("USE_OCR", "true")
    monkeypatch.setenv("FORCE_REVIEW", "1")

    with patch("qa_lab_monitor.utils.config_path", "non_existent.json"):
        cfg = utils.load_config()

    assert cfg.qa_lab_url == "http://env.com"
    assert cfg.data_points == ["dp3", "dp4"]
    assert cfg.ai_model == "gpt-3.5"
    assert cfg.use_ocr is True
    assert cfg.force_review is True


@patch("qa_lab_monitor.utils.pathlib.Path.mkdir")
@patch("qa_lab_monitor.utils.pathlib.Path.open", new_callable=mock_open)
def test_store_output_json(mock_file: MagicMock, mock_mkdir: MagicMock) -> None:
    """Test storing output as JSON."""
    data = {"key": "value"}
    utils.store_output("test_file", data, timestamp=False, format_as_json=True)

    mock_mkdir.assert_called_once_with(exist_ok=True, parents=True)

    handle = mock_file()
    assert handle.write.call_count > 0

    written_content = "".join(call.args[0] for call in handle.write.call_args_list)
    assert '"key": "value"' in written_content


@patch("qa_lab_monitor.utils.pathlib.Path.mkdir")
@patch("qa_lab_monitor.utils.pathlib.Path.open", new_callable=mock_open)
def test_store_output_string(mock_file: MagicMock, mock_mkdir: MagicMock) -> None:
    """Test storing output as plain string."""
    data = "Hello World"
    utils.store_output("test_file", data, timestamp=False, format_as_json=False)

    mock_mkdir.assert_called_once_with(exist_ok=True, parents=True)
    handle = mock_file()
    handle.write.assert_called_once_with("Hello World")
