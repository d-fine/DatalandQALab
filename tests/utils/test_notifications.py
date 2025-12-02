import json
import sys
import types
from dataclasses import dataclass

import pytest

from dataland_qa_lab.utils import notifications


@dataclass
class DummyResponse:
    status_code: int = 200
    text: str = "ok"


def make_cfg(
    environment: str | None = "prod",
    webhook_url: str | None = "https://example.com/hook",
) -> types.SimpleNamespace:
    cfg = types.SimpleNamespace()
    cfg.environment = environment
    cfg.slack_webhook_url = webhook_url
    return cfg


def test_returns_none_when_config_loading_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(notifications.config, "get_config", lambda: (_ for _ in ()).throw(Exception("boom")))
    assert notifications.send_alert_message("hi") is None


@pytest.mark.parametrize("env", ["dev", "staging", "", None, "ProdX"])
def test_returns_none_outside_production(monkeypatch: pytest.MonkeyPatch, env: str | None) -> None:
    monkeypatch.setattr(notifications.config, "get_config", lambda: make_cfg(environment=env))
    assert notifications.send_alert_message("hello") is None


@pytest.mark.parametrize("env", ["prod", "production", "PrOd", "Production"])
def test_returns_none_when_webhook_missing(monkeypatch: pytest.MonkeyPatch, env: str) -> None:
    cfg = make_cfg(environment=env, webhook_url=None)
    monkeypatch.setattr(notifications.config, "get_config", lambda: cfg)
    assert notifications.send_alert_message("hello") is None


def test_uses_explicit_webhook_and_returns_response(monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = make_cfg(environment="production", webhook_url="https://cfg/webhook")
    monkeypatch.setattr(notifications.config, "get_config", lambda: cfg)

    captured: dict[str, object] = {}

    def fake_post(url: str, data: str, headers: dict[str, str], timeout: int) -> DummyResponse:
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


def test_uses_config_webhook_when_no_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = make_cfg(environment="prod", webhook_url="https://from-config/webhook")
    monkeypatch.setattr(notifications.config, "get_config", lambda: cfg)

    captured: dict[str, object] = {}

    def fake_post(url: str, data: str, headers: dict[str, str], timeout: int) -> DummyResponse:
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


def test_returns_none_on_requests_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = make_cfg(environment="production", webhook_url="https://cfg/webhook")
    monkeypatch.setattr(notifications.config, "get_config", lambda: cfg)

    def failing_post(*args: object, **kwargs: object) -> None:  # noqa: ARG001
        msg = "network error"
        raise RuntimeError(msg)

    monkeypatch.setattr(notifications.requests, "post", failing_post)

    assert notifications.send_alert_message("This should fail") is None


def test_send_error_to_slack_formats_and_forwards(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, str] = {}

    def fake_send_alert(text: str) -> DummyResponse:
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


def test_install_global_exception_hook_sends_errors_and_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Exception] = {}

    def fake_send_error(exc: Exception) -> DummyResponse:
        captured["exc"] = exc
        return DummyResponse()

    # send_error_to_slack faken
    monkeypatch.setattr(notifications, "send_error_to_slack", fake_send_error)

    original_called: dict[str, object] = {}

    def fake_original(exc_type: type[BaseException], exc: BaseException, tb: object) -> None:
        original_called["args"] = (exc_type, exc, tb)

    # ursprünglichen excepthook faken
    monkeypatch.setattr(sys, "excepthook", fake_original)

    # unseren Hook installieren
    notifications.install_global_exception_hook()

    # „Ungefangene" Exception simulieren, indem wir den Hook direkt aufrufen
    def _raise_error() -> None:
        msg = "boom"
        raise RuntimeError(msg)

    try:
        _raise_error()
    except RuntimeError as e:
        tb = e.__traceback__
        sys.excepthook(type(e), e, tb)

    # send_error_to_slack wurde aufgerufen
    assert isinstance(captured["exc"], RuntimeError)
    # und der ursprüngliche Hook wurde auch aufgerufen
    assert original_called["args"][0] is RuntimeError
    assert original_called["args"][1] is captured["exc"]


def test_install_global_exception_hook_ignores_keyboardinterrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"send_error": False}

    def fake_send_error(exc: Exception) -> None:  # noqa: ARG001
        called["send_error"] = True

    monkeypatch.setattr(notifications, "send_error_to_slack", fake_send_error)

    original_called = {"called": False}

    def fake_original(exc_type: type[BaseException], exc: BaseException, tb: object) -> None:  # noqa: ARG001
        original_called["called"] = True

    monkeypatch.setattr(sys, "excepthook", fake_original)

    notifications.install_global_exception_hook()

    # KeyboardInterrupt soll nur an den Original-Hook gehen
    sys.excepthook(KeyboardInterrupt, KeyboardInterrupt(), None)

    assert not called["send_error"]
    assert original_called["called"]
