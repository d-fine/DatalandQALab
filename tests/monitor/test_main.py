import json
from unittest.mock import MagicMock, patch

import pytest

from monitor.categories import ESGCategory
from monitor.main import main, monitor_documents


def test_monitor_documents_success() -> None:
    """Ensure the function retrieves, parses, calls QALab API, and stores output."""
    mock_dataland = MagicMock()
    mock_dataland.model_dump_json.return_value = json.dumps({"foo": "bar"})

    with (
        patch("monitor.main.get_dataset_by_id", return_value=mock_dataland),
        patch("monitor.main.run_report_on_qalab", return_value={"ok": True}) as mock_qalab,
        patch("monitor.main.store_output") as mock_store,
    ):
        monitor_documents(documents=["123"], ai_model="gpt-4")

    mock_qalab.assert_called_once_with(data_id="123", ai_model="gpt-4", use_ocr=False)
    mock_store.assert_called_once()


def test_monitor_documents_dataset_not_found() -> None:
    """If dataset is missing, it should skip without errors."""
    with (
        patch("monitor.main.get_dataset_by_id", return_value=None),
        patch("monitor.main.run_report_on_qalab") as mock_qalab,
        patch("monitor.main.store_output") as mock_store,
    ):
        monitor_documents(documents=["missing"], ai_model="gpt-4")

    mock_qalab.assert_not_called()
    mock_store.assert_not_called()


def test_monitor_documents_invalid_json() -> None:
    """If model_dump_json returns invalid JSON, function should skip."""
    mock_dataland = MagicMock()
    mock_dataland.model_dump_json.return_value = "{invalid: json"

    with (
        patch("monitor.main.get_dataset_by_id", return_value=mock_dataland),
        patch("monitor.main.run_report_on_qalab") as mock_qalab,
        patch("monitor.main.store_output") as mock_store,
    ):
        monitor_documents(["123"], "gpt-4")

    mock_qalab.assert_not_called()
    mock_store.assert_not_called()


def test_main_no_documents_exits() -> None:
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


def test_main_successful_run() -> None:
    """Successfully running main() should call health check and monitoring."""
    mock_config = MagicMock()
    mock_config.documents = ["111", "222"]
    mock_config.ai_model = "gpt-4"

    with (
        patch("monitor.main.config", mock_config),
        patch("monitor.main.check_qalab_api_health") as mock_health,
        patch("monitor.main.monitor_documents") as mock_monitor,
    ):
        main()

    mock_health.assert_called_once()
    mock_monitor.assert_called_once_with(documents=["111", "222"], ai_model="gpt-4")


def test_monitor_documents_with_category_detection() -> None:
    """Verify category detection and ESGMonitor integration."""
    mock_dataland = MagicMock()
    mock_dataland.model_dump_json.return_value = json.dumps(
        {
            "metadata": {"type": "renewable_energy"},
            "data": {"general": {"general": {"capacity": 100}}},
        }
    )

    with (
        patch("monitor.main.get_dataset_by_id", return_value=mock_dataland),
        patch("monitor.main.run_report_on_qalab", return_value={"data": {"report": {"general": {"general": {}}}}}),
        patch("monitor.main.store_output"),
        patch("monitor.main.detect_category_from_dataset") as mock_detect,
        patch("monitor.main.ESGMonitor") as mock_monitor_class,
    ):
        mock_detect.return_value = ESGCategory.RENEWABLE_ENERGY
        mock_monitor_instance = MagicMock()
        mock_monitor_instance.validate.return_value = []
        mock_monitor_class.return_value = mock_monitor_instance

        monitor_documents(documents=["123"], ai_model="gpt-4")

        mock_detect.assert_called_once()
        mock_monitor_class.assert_called_once_with(ESGCategory.RENEWABLE_ENERGY)
        mock_monitor_instance.validate.assert_called_once()


def test_monitor_documents_uses_improved_matching() -> None:
    """Verify that improved matching function is called with category."""
    mock_dataland = MagicMock()
    mock_dataland.model_dump_json.return_value = json.dumps(
        {
            "metadata": {"type": "nuclear"},
            "data": {"general": {"general": {"field": "value"}}},
        }
    )

    with (
        patch("monitor.main.get_dataset_by_id", return_value=mock_dataland),
        patch("monitor.main.run_report_on_qalab", return_value={"data": {"report": {"general": {"general": {}}}}}),
        patch("monitor.main.store_output"),
        patch("monitor.main.detect_category_from_dataset", return_value=ESGCategory.NUCLEAR),
        patch("monitor.main.ESGMonitor"),
        patch("monitor.main.match_sot_and_qareport") as mock_match,
    ):
        mock_match.return_value = {
            "total_fields": 1,
            "matches_count": 1,
            "mismatches_count": 0,
            "skipped_count": 0,
        }

        monitor_documents(documents=["123"], ai_model="gpt-4")

        mock_match.assert_called_once()
        call_args = mock_match.call_args
        assert call_args.kwargs["category"] == "nuclear"
