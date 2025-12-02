import logging

import requests

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)


def send_alert_message(message: str) -> requests.Response | None:
    """Sends an Alert Message to the Slackbot."""
    url = config.get_config().slack_webhook_url
    environment = config.get_config().environment

    if not url:
        logger.warning("Slack webhook URL is missing in the configuration. Alert not sent. Slack message: %s", message)
        return None

    msg = f"[{environment}] {message}" if environment else message

    payload = {"text": msg}
    try:
        response = requests.post(url=url, json=payload, timeout=5)
        response.raise_for_status()

    except requests.exceptions.RequestException as exc:
        logger.warning("Failed to send alert message to Slack. Error: %s", exc)
        return None
    else:
        return response
