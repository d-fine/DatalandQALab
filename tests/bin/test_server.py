from unittest.mock import patch

from fastapi.testclient import TestClient

from dataland_qa_lab.bin.server import dataland_qa_lab, scheduler

client = TestClient(dataland_qa_lab)


def test_health_check() -> None:
    """Test /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_lifespan_shutdown() -> None:
    """Test that the scheduler shuts down correctly during lifespan exit."""
    original_shutdown = scheduler.shutdown
    called = {}

    def fake_shutdown() -> None:
        called["shutdown"] = True

    scheduler.shutdown = fake_shutdown

    with TestClient(dataland_qa_lab):
        pass

    assert called.get("shutdown") is True

    scheduler.shutdown = original_shutdown
