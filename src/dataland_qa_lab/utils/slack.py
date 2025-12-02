import requests

from dataland_qa_lab.utils import config


def send_slack_message(message: str) -> requests.Response | None:
    """Sends an Alert Message to the Slackbot."""
    url = config.get_config().slack_webhook_url
    environment = config.get_config().environment

    if url is None:
        return None

    msg = "[" + environment + "] " + message if environment else message

    payload = {"text": msg}
    response = requests.post(url=url, json=payload)

    return response
