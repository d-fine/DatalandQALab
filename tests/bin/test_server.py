from fastapi.testclient import TestClient

from unittest.mock import patch
from dataland_qa_lab.bin.server import dataland_qa_lab

client = TestClient(dataland_qa_lab)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_review_dataset_endpoint() -> None:
    mock_report = "Test report output"

    with patch("dataland_qa_lab.bin.server.review_dataset", return_value=mock_report):
        response = client.get("/review/1234?force_review=false")

    assert response.status_code == 200
    assert response.json() == mock_report
