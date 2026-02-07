from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from dataland_qa_lab.dataland import scheduled_job


@patch("dataland_qa_lab.dataland.scheduled_job.capture_checkin")
@patch("dataland_qa_lab.dataland.scheduled_job.scheduled_processor.old_run_scheduled_processing")
@patch("dataland_qa_lab.dataland.scheduled_job.data_point_scheduler.run_scheduled_processing")
@patch("dataland_qa_lab.dataland.scheduled_job.conf", new=SimpleNamespace(is_dev_environment=True))
def test_run_scheduled_processing_job_dev_success(
    mock_run_new: MagicMock,
    mock_run_old: MagicMock,
    mock_capture_checkin: MagicMock,
) -> None:
    mock_capture_checkin.return_value = "checkin-123"

    scheduled_job.run_scheduled_processing_job()

    mock_run_new.assert_called_once()
    mock_run_old.assert_not_called()

    assert mock_capture_checkin.call_count == 2
    assert mock_capture_checkin.call_args_list[0].kwargs == {
        "monitor_slug": scheduled_job.SENTRY_MONITOR_SLUG,
        "status": "in_progress",
    }
    assert mock_capture_checkin.call_args_list[1].kwargs == {
        "monitor_slug": scheduled_job.SENTRY_MONITOR_SLUG,
        "status": "ok",
        "check_in_id": "checkin-123",
    }


@patch("dataland_qa_lab.dataland.scheduled_job.capture_checkin")
@patch("dataland_qa_lab.dataland.scheduled_job.scheduled_processor.old_run_scheduled_processing")
@patch("dataland_qa_lab.dataland.scheduled_job.data_point_scheduler.run_scheduled_processing")
@patch("dataland_qa_lab.dataland.scheduled_job.conf", new=SimpleNamespace(is_dev_environment=False))
def test_run_scheduled_processing_job_non_dev_calls_old(
    mock_run_new: MagicMock,
    mock_run_old: MagicMock,
    mock_capture_checkin: MagicMock,
) -> None:
    mock_capture_checkin.return_value = "checkin-1"

    scheduled_job.run_scheduled_processing_job()

    mock_run_new.assert_not_called()
    mock_run_old.assert_called_once()


@patch("dataland_qa_lab.dataland.scheduled_job.capture_checkin")
@patch("dataland_qa_lab.dataland.scheduled_job.scheduled_processor.old_run_scheduled_processing")
@patch("dataland_qa_lab.dataland.scheduled_job.data_point_scheduler.run_scheduled_processing")
@patch("dataland_qa_lab.dataland.scheduled_job.conf", new=SimpleNamespace(is_dev_environment=True))
def test_run_scheduled_processing_job_exception_sends_error_and_reraises(
    mock_run_new: MagicMock,
    mock_run_old: MagicMock,
    mock_capture_checkin: MagicMock,
) -> None:
    mock_capture_checkin.return_value = "checkin-999"
    mock_run_new.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        scheduled_job.run_scheduled_processing_job()

    mock_run_old.assert_not_called()

    assert mock_capture_checkin.call_count == 2
    assert mock_capture_checkin.call_args_list[0].kwargs == {
        "monitor_slug": scheduled_job.SENTRY_MONITOR_SLUG,
        "status": "in_progress",
    }
    assert mock_capture_checkin.call_args_list[1].kwargs == {
        "monitor_slug": scheduled_job.SENTRY_MONITOR_SLUG,
        "status": "error",
        "check_in_id": "checkin-999",
    }
