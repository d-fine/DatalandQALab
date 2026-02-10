from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from dataland_qa_lab.bin import server
from dataland_qa_lab.data_point_flow import models as dp_models

client = TestClient(server.dataland_qa_lab)


def test_health_check() -> None:
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok"
    assert "timestamp" in json_data


@patch("dataland_qa_lab.bin.server.dataset_reviewer.old_review_dataset_via_api")
@patch("dataland_qa_lab.bin.server.get_german_time_as_string")
def test_review_dataset_post_endpoint_success(mock_time: MagicMock, mock_reviewer: MagicMock) -> None:
    """Test the /review/{data_id} endpoint for successful review."""
    mock_reviewer.return_value = {"dp1": "ok"}
    mock_time.return_value = "2025-12-11 12:00:00"

    response = client.post("/review/dataset123", json={"ai_model": "gpt-4", "force_review": True, "use_ocr": True})
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"] == {"dp1": "ok"}
    assert json_data["meta"]["timestamp"] == "2025-12-11 12:00:00"


@patch("dataland_qa_lab.bin.server.review.validate_datapoint", new_callable=AsyncMock)
@patch("dataland_qa_lab.bin.server.config")
def test_review_data_point_id_sync(mock_config: MagicMock, mock_validate: AsyncMock) -> None:
    """Test async /review-data-point endpoint."""
    mock_config.get_config.return_value.dataland_client = MagicMock()

    async def mock_validate_response(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202, ARG001, RUF029
        return dp_models.ValidatedDatapoint(
            data_point_id="dp1",
            data_point_type="number",
            previous_answer=10,
            predicted_answer=10,
            confidence=1.0,
            reasoning="ok",
            qa_status="QaAccepted",
            timestamp=1,
            ai_model="gpt-4",
            use_ocr=True,
            file_name="file.pdf",
            file_reference="ref1",
            page=1,
            qa_report_id="test",
            override=False,
            _prompt="prompt text",
        )

    mock_validate.side_effect = mock_validate_response

    response = client.post(
        "/data-point-flow/review-data-point/dp1",
        json={"ai_model": "gpt-4", "use_ocr": True, "override": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data_point_id"] == "dp1"
    assert data["qa_status"] == "QaAccepted"


def test_init_sentry_skips_when_no_dsn() -> None:
    server.conf = SimpleNamespace(sentry_dsn=None, environment="dev")
    with patch.object(server.sentry_sdk, "init") as sentry_init:
        server.init_sentry()
        sentry_init.assert_not_called()


def test_init_sentry_calls_sentry_when_dsn_present() -> None:
    server.conf = SimpleNamespace(sentry_dsn="https://example@dsn/1", environment="dev")
    with patch.object(server.sentry_sdk, "init") as sentry_init:
        server.init_sentry()
        sentry_init.assert_called_once()


def test_init_sentry_handles_bad_dsn() -> None:
    server.conf = SimpleNamespace(sentry_dsn="bad", environment="dev")
    with patch.object(server.sentry_sdk, "init", side_effect=server.BadDsn("bad dsn")) as sentry_init:
        server.init_sentry()
        sentry_init.assert_called_once()
