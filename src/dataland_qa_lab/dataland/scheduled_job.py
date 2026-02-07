import logging

from sentry_sdk.crons.api import capture_checkin

from dataland_qa_lab.data_point_flow import scheduler as data_point_scheduler
from dataland_qa_lab.dataland import scheduled_processor
from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)
conf = config.get_config()

SENTRY_MONITOR_SLUG = "dataland-scheduler-heartbeat"


def run_scheduled_processing_job() -> None:
    """Single scheduled entry point. Sends Sentry cron check-ins and then delegates to the active implementation."""
    check_in_id = None
    try:
        check_in_id = capture_checkin(
            monitor_slug=SENTRY_MONITOR_SLUG,
            status="in_progress",
        )

        if conf.is_dev_environment:
            data_point_scheduler.run_scheduled_processing()
        else:
            scheduled_processor.old_run_scheduled_processing()

        capture_checkin(
            monitor_slug=SENTRY_MONITOR_SLUG,
            status="ok",
            check_in_id=check_in_id,
        )
        logger.info("Sentry cron check-in sent: ok")

    except Exception:
        logger.exception("Scheduled processing failed.")

        if check_in_id is not None:
            capture_checkin(
                monitor_slug=SENTRY_MONITOR_SLUG,
                status="error",
                check_in_id=check_in_id,
            )
            logger.info("Sentry cron check-in sent: error")
        raise
