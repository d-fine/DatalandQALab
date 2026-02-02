import hashlib
import logging

import sentry_sdk
from sentry_sdk.utils import BadDsn

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)


def send_slack_message(message: str) -> None:
    """Create a notification event in Sentry (Sentry forwards to Slack)."""
    cfg = config.get_config()
    env = getattr(cfg, "environment", None)
    msg = f"[{env.upper()}] {message}" if env else message

    try:
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("notify", "slack")
            msg_hash = hashlib.sha256(msg.encode("utf-8")).hexdigest()[:12]
            scope.fingerprint = ["slack-notify", msg_hash]
            sentry_sdk.capture_message(msg, level="info")
    except BadDsn as e:
        logger.warning("Failed to send notification to Sentry: %s", e)
    except Exception as e:  # noqa: BLE001
        logger.warning("Failed to send notification to Sentry: %s", e)
