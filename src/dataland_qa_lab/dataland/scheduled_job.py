import logging

from dataland_qa_lab.data_point_flow import scheduler as data_point_scheduler
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)
_cfg = config.get_config()

SENTRY_MONITOR_SLUG = "dataland-scheduler-heartbeat"

try:
    from sentry_sdk.crons.api import capture_checkin
except Exception:  # noqa: BLE001
    capture_checkin = None


def run_scheduled_processing_job() -> None:
    """Single scheduled entry point. Sends Sentry cron check-ins and then delegates to the active implementation."""
    check_in_id = None
    try:
        if capture_checkin is not None:
            check_in_id = capture_checkin(
                monitor_slug=SENTRY_MONITOR_SLUG,
                status="in_progress",
            )

        if _cfg.is_dev_environment:
            data_point_scheduler.run_scheduled_processing()
        else:
            scheduled_processor.old_run_scheduled_processing()

        if capture_checkin is not None and check_in_id is not None:
            capture_checkin(
                monitor_slug=SENTRY_MONITOR_SLUG,
                status="ok",
                check_in_id=check_in_id,
            )
            logger.info("Sentry cron check-in sent: ok")

    except Exception:
        logger.exception("Scheduled processing failed.")
        if capture_checkin is not None and check_in_id is not None:
            capture_checkin(
                monitor_slug=SENTRY_MONITOR_SLUG,
                status="error",
                check_in_id=check_in_id,
            )
            logger.info("Sentry cron check-in sent: error")
        raise
