import json
import logging

import requests

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)


def send_alert_message(message: str) -> requests.Response | None:
    """Sends an Alert Message to the Slackbot."""
    conf = config.get_config()
    url: str | None = conf.slack_webhook_url
    environment: str | None = conf.environment

    if not url:
        logger.debug("Skipping alert message: No Slack Webhook URL configured.")
        return None

    msg = message if environment is None else "[" + environment + "] " + message

    payload = {"text": msg}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url=url, data=json.dumps(payload), headers=headers)
        return response
    except Exception as e:
        # Alerting sollte niemals die Hauptanwendung crashen lassen
        logger.warning("Failed to send alert message: %s", e)
        return None
