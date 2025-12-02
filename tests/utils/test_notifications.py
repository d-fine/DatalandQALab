import json
import types
import pytest
from dataland_qa_lab.utils import notifications
import sys

class DummyResponse:
    def __init__(self, status_code=200, text="ok"):
        self.status_code = status_code
        self.text = text


def make_cfg(environment="prod", webhook_url="https://example.com/hook"):
    cfg = types.SimpleNamespace()
    cfg.environment = environment
    cfg.slack_webhook_url = webhook_url
    return cfg


def test_returns_none_when_config_loading_fails(monkeypatch):
    monkeypatch.setattr(notifications.config, "get_config", lambda: (_ for _ in ()).throw(Exception("boom")))
    assert notifications.send_alert_message("hi") is None


@pytest.mark.parametrize("env", ["dev", "staging", "", None, "ProdX"])
def test_returns_none_outside_production(monkeypatch, env):
    monkeypatch.setattr(notifications.config, "get_config", lambda: make_cfg(environment=env))
    assert notifications.send_alert_message("hello") is None


@pytest.mark.parametrize("env", ["prod", "production", "PrOd", "Production"])
def test_returns_none_when_webhook_missing(monkeypatch, env):
    cfg = make_cfg(environment=env, webhook_url=None)
    monkeypatch.setattr(notifications.config, "get_config", lambda: cfg)
    assert notifications.send_alert_message("hello") is None


def test_uses_explicit_webhook_and_returns_response(monkeypatch):
    cfg = make_cfg(environment="production", webhook_url="https://cfg/webhook")
    monkeypatch.setattr(notifications.config, "get_config", lambda: cfg)

    captured = {}

    def fake_post(url, data, headers, timeout):
        captured["url"] = url
        captured["data"] = data
        captured["headers"] = headers
        captured["timeout"] = timeout
        return DummyResponse(200, "ok")

    monkeypatch.setattr(notifications.requests, "post", fake_post)

    resp = notifications.send_alert_message("Alert body", webhook_url="https://explicit/webhook")
    assert isinstance(resp, DummyResponse)

    # Explicit webhook takes precedence over config
    assert captured["url"] == "https://explicit/webhook"

    # Payload and headers
    payload = json.loads(captured["data"])
    assert payload["text"].startswith("[production] ")
    assert payload["text"].endswith("Alert body")
    assert captured["headers"] == {"Content-Type": "application/json"}
    assert captured["timeout"] == 5


def test_uses_config_webhook_when_no_explicit(monkeypatch):
    cfg = make_cfg(environment="prod", webhook_url="https://from-config/webhook")
    monkeypatch.setattr(notifications.config, "get_config", lambda: cfg)

    captured = {}

    def fake_post(url, data, headers, timeout):
        captured["url"] = url
        captured["data"] = data
        captured["headers"] = headers
        captured["timeout"] = timeout
        return DummyResponse(201, "created")

    monkeypatch.setattr(notifications.requests, "post", fake_post)

    resp = notifications.send_alert_message("Msg without explicit webhook")
    assert isinstance(resp, DummyResponse)
    assert captured["url"] == "https://from-config/webhook"

    payload = json.loads(captured["data"])
    # Prefix uses original case from cfg.environment (here "prod")
    assert payload["text"].startswith("[prod] ")
    assert "Msg without explicit webhook" in payload["text"]


def test_returns_none_on_requests_exception(monkeypatch):
    cfg = make_cfg(environment="production", webhook_url="https://cfg/webhook")
    monkeypatch.setattr(notifications.config, "get_config", lambda: cfg)

    def failing_post(*args, **kwargs):
        raise RuntimeError("network error")

    monkeypatch.setattr(notifications.requests, "post", failing_post)

    assert notifications.send_alert_message("This should fail") is None

def test_send_error_to_slack_formats_and_forwards(monkeypatch):
    captured = {}

    def fake_send_alert(text):
        captured["text"] = text
        return DummyResponse(204, "")

    # send_error_to_slack soll nur send_alert_message aufrufen
    monkeypatch.setattr(notifications, "send_alert_message", fake_send_alert)

    exc = ValueError("bad value")
    resp = notifications.send_error_to_slack(exc, prefix="PREFIX")

    # Rückgabewert wird von send_alert_message durchgereicht
    assert isinstance(resp, DummyResponse)

    # Nachricht enthält Prefix, Typ, Message und Code-Block
    assert "PREFIX" in captured["text"]
    assert "ValueError" in captured["text"]
    assert "bad value" in captured["text"]
    assert captured["text"].count("```") == 2

def test_install_global_exception_hook_sends_errors_and_delegates(monkeypatch):
    captured = {}

    def fake_send_error(exc):
        captured["exc"] = exc
        return DummyResponse()

    # send_error_to_slack faken
    monkeypatch.setattr(notifications, "send_error_to_slack", fake_send_error)

    original_called = {}

    def fake_original(exc_type, exc, tb):
        original_called["args"] = (exc_type, exc, tb)

    # ursprünglichen excepthook faken
    monkeypatch.setattr(sys, "excepthook", fake_original)

    # unseren Hook installieren
    notifications.install_global_exception_hook()

    # „Ungefangene“ Exception simulieren, indem wir den Hook direkt aufrufen
    try:
        raise RuntimeError("boom")
    except RuntimeError as e:
        tb = e.__traceback__
        sys.excepthook(type(e), e, tb)

    # send_error_to_slack wurde aufgerufen
    assert isinstance(captured["exc"], RuntimeError)
    # und der ursprüngliche Hook wurde auch aufgerufen
    assert original_called["args"][0] is RuntimeError
    assert original_called["args"][1] is captured["exc"]


def test_install_global_exception_hook_ignores_keyboardinterrupt(monkeypatch):
    called = {"send_error": False}

    def fake_send_error(exc):
        called["send_error"] = True

    monkeypatch.setattr(notifications, "send_error_to_slack", fake_send_error)

    original_called = {"called": False}

    def fake_original(exc_type, exc, tb):
        original_called["called"] = True

    monkeypatch.setattr(sys, "excepthook", fake_original)

    notifications.install_global_exception_hook()

    # KeyboardInterrupt soll nur an den Original-Hook gehen
    sys.excepthook(KeyboardInterrupt, KeyboardInterrupt(), None)

    assert not called["send_error"]
    assert original_called["called"]