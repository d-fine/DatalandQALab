import json
import sys
import traceback

import requests

from dataland_qa_lab.utils import config


def send_alert_message(text: str, webhook_url: str | None = None) -> requests.Response | None:
    """Send a simple alert message to Slack via webhook.

    - Active only if config.environment is prod/production (case-insensitive)
    - Webhook URL resolved from `webhook_url` override or config.slack_webhook_url
    - Returns the requests.Response on success; None if skipped or on failure
    - Fails silently if misconfigured or on network errors
    """
    # Load configuration once
    try:
        cfg = config.get_config()
    except Exception:  # noqa: BLE001
        return None

    environment = (getattr(cfg, "environment", None) or "").lower()
    if environment not in {"prod", "production"}:
        return None

    # Resolve webhook URL (explicit arg takes precedence if provided)
    url = webhook_url or getattr(cfg, "slack_webhook_url", None)
    if not url:
        return None

    # Add environment prefix for context (use original case if available)
    env_prefix = getattr(cfg, "environment", None)
    message = text if not env_prefix else f"[{env_prefix}] {text}"

    payload = {"text": message}
    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(url=url, data=json.dumps(payload), headers=headers, timeout=5)
    except Exception:  # noqa: BLE001
        # Do not raise further; this is best-effort alerting
        return None
    else:
        return resp


def send_error_to_slack(exc: Exception, prefix: str = "❌ QA Lab crashed") -> requests.Response | None:
    """Format an exception and send it to Slack.

    Includes type, message, and a shortened traceback in a Markdown code block.
    Silently no-ops outside production or when webhook is missing.
    """
    # Build a compact traceback (first and last few lines)
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    tb_text = "".join(tb_lines)

    # Trim very long traces: keep head and tail
    max_chars = 3000
    if len(tb_text) > max_chars:
        head = tb_text[:1500]
        tail = tb_text[-1200:]
        tb_text = f"{head}\n...\n{tail}"

    lines = [
        prefix,
        f"Type: {type(exc).__name__}",
        f"Message: {exc!s}",
        "```",  # Markdown code block
        tb_text.strip(),
        "```",
    ]
    text = "\n".join(lines)

    return send_alert_message(text)


def install_global_exception_hook() -> None:
    """Install a global exception hook that forwards uncaught exceptions to Slack.

    - Ignores KeyboardInterrupt to allow graceful shutdowns
    - Calls the original excepthook after attempting to send the alert
    """
    original_hook = sys.excepthook

    def _custom_handler(exc_type, exc, tb) -> None:  # noqa: ANN001
        if exc_type is KeyboardInterrupt:
            # Pass through without alerting
            original_hook(exc_type, exc, tb)
            return

        try:
            # Create an Exception instance with its traceback
            exc.__traceback__ = tb  # type: ignore[attr-defined]
            send_error_to_slack(exc)
        except Exception:  # noqa: BLE001
            # Never let alerting crash the process
            pass
        # Always delegate to original hook (logging/printing)
        original_hook(exc_type, exc, tb)

    sys.excepthook = _custom_handler
