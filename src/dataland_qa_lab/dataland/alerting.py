import json
import logging

import requests

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)


def send_alert_message(message: str) -> requests.Response | None:
    """Send an alert message to Slack if a webhook is configured.

    Wenn die Slack Webhook URL fehlt oder ungültig ist,
    wird nur eine Warnung geloggt und keine Exception geworfen.
    """
    url: str | None = config.get_config().slack_webhook_url
    environment: str | None = config.get_config().environment

    # Kein Webhook gesetzt oder leer
    if not url:
        logger.warning(
            "Slack webhook URL missing oder leer (config.slack_webhook_url). "
            "Slack Alert wird übersprungen. Nachricht war: %s",
            message,
        )
        return None

    # Umgebung vor die Nachricht hängen
    msg = f"[{environment}] {message}" if environment else message

    payload = {"text": msg}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url=url, data=json.dumps(payload), headers=headers, timeout=5)

        # Slack Antwort mit Fehlercode
        if response.status_code >= 400:
            logger.warning(
                "Slack webhook Antwort mit HTTP %s. Response Text: %s",
                response.status_code,
                response.text,
            )
            return None

        return response

    except Exception as exc:
        logger.warning(
            "Slack webhook Request fehlgeschlagen. Slack Alert wird übersprungen. Exception: %s",
            exc,
        )
        return None
