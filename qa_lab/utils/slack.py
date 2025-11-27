import json
from logging import getLogger

import requests

from qa_lab.utils.config import get_config

conf = get_config()
logger = getLogger(__name__)


def send_slack_message(message: str) -> None:
    """Sends an Alert Message to the Slackbot."""
    payload = {"text": message}
    headers = {"Content-Type": "application/json"}

    res = requests.request(
        "POST",
        url=conf.slack_webhook_url or "https://example.com",
        data=json.dumps(payload),
        headers=headers,
    )
    if res.status_code is not requests.codes.ok:
        logger.error("Failed to send Slack message: %s", res.text)
