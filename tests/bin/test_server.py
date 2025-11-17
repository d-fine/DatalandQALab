from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from dataland_qa_lab.bin.server import dataland_qa_lab

client = TestClient(dataland_qa_lab)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.slow  # this test case would take around 1:30min since it runs all the codes logic
@patch("src.dataland_qa_lab.bin.server.review_dataset_endpoint")
def test_review_dataset_endpoint() -> None:  # noqa: ANN001
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

    assert body["force_override"] is False
    assert body["use_ocr"] is True
    assert body["ai_model"] == "gpt-4"
