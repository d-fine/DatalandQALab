import json

import requests

from dataland_qa_lab.utils import config

url: str | None = config.get_config().slack_webhook_url
environment: str | None = config.get_config().environment


def send_alert_message(message: str) -> requests.Response:
    """Sends an Alert Message to the Slackbot."""
    msg = "[" + environment + "] " + message

    payload = {"text": msg}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, data=json.dumps(payload), headers=headers)

    return response
