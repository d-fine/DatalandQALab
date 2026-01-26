import logging

import sentry_sdk
from sentry_sdk.utils import BadDsn

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)


def send_slack_message(message: str) -> None:
    """Create a notification event in Sentry (Sentry forwards to Slack)."""
    cfg = config.get_config()
    environment = getattr(cfg, "environment", None)
    msg = f"[{environment}] {message}" if environment else message

    try:
        sentry_sdk.capture_message(f"Notification: {msg}", level="warning")
    except BadDsn as e:
        logger.warning("Failed to send notification to Sentry: %s", e)
    except Exception as e:  # noqa: BLE001
        logger.warning("Failed to send notification to Sentry: %s", e)
