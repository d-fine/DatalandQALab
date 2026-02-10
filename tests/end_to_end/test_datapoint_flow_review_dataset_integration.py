"""End-to-end tests for the data point flow review dataset endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from dataland_qa.models.qa_status import QaStatus
from fastapi.testclient import TestClient

from dataland_qa_lab.bin.server import app
from dataland_qa_lab.data_point_flow.models import ValidatedDatapoint


@pytest.fixture
def test_client() -> TestClient:
    """Provide a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_validated_datapoint() -> ValidatedDatapoint:
    """Provide a mock validated datapoint."""
    return ValidatedDatapoint(
        data_point_id="dp_1",
        data_point_type="numeric",
        previous_answer="100",
        predicted_answer="105",
        confidence=0.95,
        reasoning="Based on document analysis",
        qa_status=QaStatus.ACCEPTED,
        ai_model="gpt-4o",
        use_ocr=False,
        override=False,
        file_name="test.pdf",
        file_reference="ref_1",
        page=1,
        _prompt=None,
        timestamp=1234567890,
        qa_report_id="qa_report_1",
    )


def test_review_dataset_returns_200_with_datapoint_results(
    test_client: TestClient, mock_validated_datapoint: ValidatedDatapoint
) -> None:
    """Test that the endpoint returns HTTP 200 with validation results for each datapoint."""
    data_id = "dataset_123"

    mock_datapoints = {
        "scope1": "dp_1",
        "scope2": "dp_2",
    }

    mock_validated_datapoint_2 = ValidatedDatapoint(
        data_point_id="dp_2",
        data_point_type="numeric",
        previous_answer="200",
        predicted_answer="210",
        confidence=0.92,
        reasoning="Based on historical data",
        qa_status=QaStatus.ACCEPTED,
        ai_model="gpt-4o",
        use_ocr=False,
        override=False,
        file_name="test2.pdf",
        file_reference="ref_2",
        page=2,
        _prompt=None,
        timestamp=1234567891,
        qa_report_id="qa_report_2",
    )

    with (
        patch(
            "dataland_qa_lab.bin.server.dataland.get_contained_data_points", new_callable=AsyncMock
        ) as mock_get_datapoints,
        patch("dataland_qa_lab.bin.server.review.validate_datapoint", new_callable=AsyncMock) as mock_validate,
    ):
        mock_get_datapoints.return_value = mock_datapoints
        mock_validate.side_effect = [mock_validated_datapoint, mock_validated_datapoint_2]

        response = test_client.post(
            f"/data-point-flow/review-dataset/{data_id}",
            json={
                "ai_model": "gpt-4o",
                "use_ocr": False,
                "override": False,
            },
        )

        assert response.status_code == 200

        response_data = response.json()
        assert "scope1" in response_data
        assert "scope2" in response_data

        scope1_result = response_data["scope1"]
        assert scope1_result["data_point_id"] == "dp_1"
        assert scope1_result["qa_status"] == QaStatus.ACCEPTED
        assert scope1_result["confidence"] == 0.95

        scope2_result = response_data["scope2"]
        assert scope2_result["data_point_id"] == "dp_2"
        assert scope2_result["qa_status"] == QaStatus.ACCEPTED
        assert scope2_result["confidence"] == 0.92

        assert mock_validate.await_count == 2
        mock_validate.assert_any_await("dp_1", use_ocr=False, ai_model="gpt-4o", override=False, dataset_id=data_id)
        mock_validate.assert_any_await("dp_2", use_ocr=False, ai_model="gpt-4o", override=False, dataset_id=data_id)


def test_review_dataset_empty_datapoints(test_client: TestClient) -> None:
    """Test that the endpoint handles empty datapoint lists correctly."""
    data_id = "dataset_empty"

    with patch(
        "dataland_qa_lab.bin.server.dataland.get_contained_data_points", new_callable=AsyncMock
    ) as mock_get_datapoints:
        mock_get_datapoints.return_value = {}

        response = test_client.post(
            f"/data-point-flow/review-dataset/{data_id}",
            json={
                "ai_model": "gpt-4o",
                "use_ocr": False,
                "override": False,
            },
        )

        assert response.status_code == 200
        assert response.json() == {}


def test_review_dataset_with_validation_error(
    test_client: TestClient, mock_validated_datapoint: ValidatedDatapoint
) -> None:
    """Test that validation errors from validate_datapoint propagate out of the endpoint.

    Note: Exceptions from validate_datapoint propagate through asyncio.gather and are
    converted to HTTP 500 errors by FastAPI when the endpoint is called normally. When
    invoked via TestClient, these exceptions are re-raised instead of returning a 500
    response, so this test asserts that the underlying RuntimeError is raised.
    """
    data_id = "dataset_with_error"

    mock_datapoints = {
        "scope1": "dp_1",
        "scope2": "dp_2",
    }

    with (
        patch(
            "dataland_qa_lab.bin.server.dataland.get_contained_data_points", new_callable=AsyncMock
        ) as mock_get_datapoints,
        patch("dataland_qa_lab.bin.server.review.validate_datapoint", new_callable=AsyncMock) as mock_validate,
    ):
        mock_get_datapoints.return_value = mock_datapoints
        mock_validate.side_effect = [
            mock_validated_datapoint,
            RuntimeError("Validation failed for dp_2"),
        ]

        # The endpoint will raise an unhandled exception, which TestClient re-raises
        with pytest.raises(RuntimeError, match="Validation failed for dp_2"):
            test_client.post(
                f"/data-point-flow/review-dataset/{data_id}",
                json={
                    "ai_model": "gpt-4o",
                    "use_ocr": False,
                    "override": False,
                },
            )


def test_review_dataset_passes_custom_ai_model(
    test_client: TestClient, mock_validated_datapoint: ValidatedDatapoint
) -> None:
    """Test that custom ai_model and use_ocr parameters are passed correctly."""
    data_id = "dataset_custom_params"

    mock_datapoints = {
        "scope1": "dp_1",
    }

    with (
        patch(
            "dataland_qa_lab.bin.server.dataland.get_contained_data_points", new_callable=AsyncMock
        ) as mock_get_datapoints,
        patch("dataland_qa_lab.bin.server.review.validate_datapoint", new_callable=AsyncMock) as mock_validate,
    ):
        mock_get_datapoints.return_value = mock_datapoints
        mock_validate.return_value = mock_validated_datapoint

        response = test_client.post(
            f"/data-point-flow/review-dataset/{data_id}",
            json={
                "ai_model": "gpt-3.5-turbo",
                "use_ocr": True,
                "override": True,
            },
        )

        assert response.status_code == 200

        mock_validate.assert_awaited_once_with(
            "dp_1",
            use_ocr=True,
            ai_model="gpt-3.5-turbo",
            override=True,
            dataset_id=data_id,
        )
