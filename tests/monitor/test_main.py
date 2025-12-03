import json
from unittest.mock import MagicMock, patch

import pytest

from monitor.main import main, monitor_documents


@pytest.fixture
def mock_framework() -> MagicMock:
    return MagicMock()


def test_monitor_documents_success(mock_framework: MagicMock) -> None:
    """Ensure the function retrieves, parses, calls QALab API, and stores output."""
    mock_dataland = MagicMock()
    mock_dataland.model_dump_json.return_value = json.dumps({"foo": "bar"})

    with (
        patch("monitor.main.get_dataset_by_id", return_value=mock_dataland),
        patch("monitor.main.run_report_on_qalab", return_value={"ok": True}) as mock_qalab,
        patch("monitor.main.store_output") as mock_store,
    ):
        monitor_documents(documents=["123"], ai_model="gpt-4", framework=mock_framework)

    mock_qalab.assert_called_once_with(data_id="123", ai_model="gpt-4", use_ocr=False)
    mock_store.assert_called_once()


def test_monitor_documents_dataset_not_found(mock_framework: MagicMock) -> None:
    """If dataset is missing, it should skip without errors."""
    with (
        patch("monitor.main.get_dataset_by_id", return_value=None),
        patch("monitor.main.run_report_on_qalab") as mock_qalab,
        patch("monitor.main.store_output") as mock_store,
    ):
        monitor_documents(documents=["missing"], ai_model="gpt-4", framework=mock_framework)

    mock_qalab.assert_not_called()
    mock_store.assert_not_called()


def test_monitor_documents_invalid_json(mock_framework: MagicMock) -> None:
    """If model_dump_json returns invalid JSON, function should skip."""
    mock_dataland = MagicMock()
    mock_dataland.model_dump_json.return_value = "{invalid: json"

    with (
        patch("monitor.main.get_dataset_by_id", return_value=mock_dataland),
        patch("monitor.main.run_report_on_qalab") as mock_qalab,
        patch("monitor.main.store_output") as mock_store,
    ):
        monitor_documents(["123"], "gpt-4", framework=mock_framework)

    mock_qalab.assert_not_called()
    mock_store.assert_not_called()


def test_main_no_documents_exits(mock_framework: MagicMock) -> None:
    """If config.documents is empty, main() must call sys.exit(1)."""
    mock_config = MagicMock()
    mock_config.documents = []
    mock_config.ai_model = "gpt-4"

    with (
        patch("monitor.main.config", mock_config),
        patch("monitor.main.check_qalab_api_health"),
    ):
        with pytest.raises(SystemExit) as exit_info:
            main()
        assert exit_info.value.code == 1


def test_main_successful_run(mock_framework: MagicMock) -> None:
    """Successfully running main() should call health check and monitoring."""
    mock_config = MagicMock()
    mock_config.documents = ["111", "222"]
    mock_config.ai_model = "gpt-4"

    with (
        patch("monitor.main.config", mock_config),
        patch("monitor.main.check_qalab_api_health") as mock_health,
        patch(
            "monitor.main.monitor_documents",
            wraps=lambda documents, ai_model: monitor_documents(
                documents, ai_model, framework=mock_framework
            ),
        ) as mock_monitor,
    ):
        main()

    mock_health.assert_called_once()
    mock_monitor.assert_called_once_with(documents=["111", "222"], ai_model="gpt-4")
