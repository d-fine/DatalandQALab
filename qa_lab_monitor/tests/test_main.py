# tests/test_main.py
from unittest.mock import MagicMock, patch

import pytest

from qa_lab_monitor.main import analytics, main, monitor_data_points

sample_data_points = ["dp1", "dp2"]
mock_responses = {
    "dp1": {"qa_status": "Accepted", "confidence": 0.9},
    "dp2": {"qa_status": "Rejected", "confidence": 0.7},
}


@pytest.fixture(autouse=True)
def reset_analytics():
    """Reset analytics Counter before each test."""
    analytics.clear()
    analytics.update(
        {
            "total_fields": 0,
            "qa_accepted": 0,
            "qa_rejected": 0,
            "qa_pending": 0,
            "average_confidence": 0,
        }
    )
    yield
    analytics.clear()


@patch("qa_lab_monitor.main.review_data_point_on_qalab")
@patch("qa_lab_monitor.main.store_output")
def test_monitor_data_points(mock_store: MagicMock, mock_review: MagicMock) -> None:
    """Test monitor_data_points updates analytics correctly."""
    mock_review.side_effect = lambda data_point_id, ai_model, use_ocr: mock_responses[data_point_id]  # noqa: ARG005

    # Dummy config object
    mock_config = MagicMock()
    mock_config.use_ocr = False

    monitor_data_points(sample_data_points, "test_model", config=mock_config)

    assert mock_review.call_count == 2
    assert mock_store.call_count == 2

    assert analytics["total_fields"] == 2
    assert analytics["qa_accepted"] == 1
    assert analytics["qa_rejected"] == 1
    assert analytics["qa_pending"] == 0
    assert analytics["average_confidence"] == pytest.approx(1.6)


@patch("qa_lab_monitor.main.load_config")
@patch("qa_lab_monitor.main.store_output")
@patch("qa_lab_monitor.main.monitor_data_points")
@patch("qa_lab_monitor.main.check_qalab_api_health")
def test_main_flow(
    mock_health: MagicMock, mock_monitor: MagicMock, mock_store: MagicMock, mock_load_config: MagicMock
) -> None:
    """Test the full main() flow."""
    mock_cfg = MagicMock()
    mock_cfg.data_points = sample_data_points
    mock_cfg.ai_model = "test_model"
    mock_cfg.use_ocr = False
    mock_load_config.return_value = mock_cfg

    main()

    # Now it patches the correct references inside main.py
    mock_health.assert_called_once()
    mock_monitor.assert_called_once_with(data_points=sample_data_points, ai_model="test_model", config=mock_cfg)
    assert mock_store.called


def test_main_no_data_points(monkeypatch: MagicMock) -> None:
    """Test main exits if no data points are provided."""
    mock_cfg = MagicMock()
    mock_cfg.data_points = []
    mock_cfg.ai_model = "test_model"
    mock_cfg.use_ocr = False

    monkeypatch.setattr("qa_lab_monitor.main.load_config", lambda: mock_cfg)

    with pytest.raises(SystemExit) as e:
        main()
    assert e.type is SystemExit
    assert e.value.code == 1
