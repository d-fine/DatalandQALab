import json

import requests

from dataland_qa_lab.utils import config


def send_alert_message(message: str) -> requests.Response | None:
    """Sends an Alert Message to the Slackbot."""
    url: str | None = config.get_config().slack_webhook_url
    environment: str | None = config.get_config().environment
    if url is None:
        return None

    msg = message if environment is None else "[" + environment + "] " + message

    payload = {"text": msg}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, data=json.dumps(payload), headers=headers)

    return response
