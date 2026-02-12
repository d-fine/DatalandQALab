from unittest.mock import MagicMock, patch

import pytest

from dataland_qa_lab.dataland import scheduled_job


@patch("dataland_qa_lab.dataland.scheduled_job.capture_checkin")
def test_run_scheduled_processing_job_success(mock_capture_checkin: MagicMock) -> None:
    mock_capture_checkin.return_value = "checkin-123"
    run_impl = MagicMock()

    scheduled_job.run_scheduled_processing_job(run_impl)

    run_impl.assert_called_once()

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
def test_run_scheduled_processing_job_exception_sends_error_and_reraises(
    mock_capture_checkin: MagicMock,
) -> None:
    mock_capture_checkin.return_value = "checkin-999"
    run_impl = MagicMock(side_effect=RuntimeError("boom"))

    with pytest.raises(RuntimeError, match="boom"):
        scheduled_job.run_scheduled_processing_job(run_impl)

    run_impl.assert_called_once()

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
