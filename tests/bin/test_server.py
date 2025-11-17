from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from dataland_qa_lab.bin.server import dataland_qa_lab, scheduler

client = TestClient(dataland_qa_lab)


def test_health_check() -> None:
    """Test /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_review_dataset_endpoint() -> None:
    data_id = "2faf0140-b338-47ec-9c7f-276209f63e95"

    with patch("src.dataland_qa_lab.bin.server.review_dataset_via_api") as mock_review:
        mock_review.return_value = {
            "report_data": {"fake": "data"},
            "start_time": 123456,
            "end_time": 123457,
            "force_override": False,
            "use_ocr": True,
            "ai_model": "gpt-4",
        }

        response = client.get(f"/review/{data_id}?force_override=false&use_ocr=true&ai_model=gpt-4")

    assert response.status_code == 200
    body = response.json()

    assert body["report_data"] == {"fake": "data"}
    assert body["force_override"] is False
    assert body["use_ocr"] is True
    assert body["ai_model"] == "gpt-4"


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
