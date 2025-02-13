import json
import os

import requests

url = os.getenv("SLACK_WEBHOOK_URL")


def send_alert_message(message: str) -> requests.Response:
    """Sends an Alert Message to the Slackbot."""
    payload = {"text": message}

    headers = {"Content-Type": "application/json"}

    response = requests.post(url=url, data=json.dumps(payload), headers=headers)

    return response
