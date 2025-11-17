from fastapi.testclient import TestClient

from dataland_qa_lab.bin.server import dataland_qa_lab, scheduler

client = TestClient(dataland_qa_lab)


def test_health_check() -> None:
    """Test /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# this test case would take around 1:30min since it runs all the codes logic
def test_review_dataset_endpoint() -> None:
    """Test the /review/{data_id} endpoint."""
    data_id = "2faf0140-b338-47ec-9c7f-276209f63e95"

    response = client.get(f"/review/{data_id}?force_override=false&use_ocr=true&ai_model=gpt-4")

    assert response.status_code == 200
    body = response.json()

    assert "report_data" in body
    assert "start_time" in body
    assert "end_time" in body
    assert "force_override" in body
    assert "use_ocr" in body
    assert "ai_model" in body

    assert isinstance(body["start_time"], int)
    assert isinstance(body["end_time"], int)
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
