from __future__ import annotations

import collections.abc  # noqa: TC003
import logging

from sentry_sdk.crons.api import capture_checkin

logger = logging.getLogger(__name__)

SENTRY_MONITOR_SLUG = "dataland-scheduler-heartbeat"


def run_scheduled_processing_job(run_impl: collections.abc.Callable[[], None]) -> None:
    """Single scheduled entry point. Sends Sentry cron check-ins and then runs the given implementation."""
    check_in_id = None
    try:
        check_in_id = capture_checkin(
            monitor_slug=SENTRY_MONITOR_SLUG,
            status="in_progress",
        )

        run_impl()

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
