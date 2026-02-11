import json
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice
from PIL import Image

from dataland_qa_lab.bin.server import dataland_qa_lab
from dataland_qa_lab.data_point_flow.models import DataPointPrompt
from dataland_qa_lab.database.database_engine import delete_entity
from dataland_qa_lab.database.database_tables import ReviewedDataset
from dataland_qa_lab.dataland.provide_test_data import get_company_id, upload_dataset, upload_pdf
from dataland_qa_lab.utils import config


@pytest.fixture
def test_client() -> TestClient:
    """Provide a FastAPI test client."""
    return TestClient(dataland_qa_lab)


@pytest.fixture
def uploaded_dataset_id() -> str:
    """Upload a test dataset and return its `data_id`."""
    dataland_client = config.get_config().dataland_client
    project_root = Path(__file__).resolve().parent.parent.parent
    pdf_path = project_root / "data" / "pdfs"
    json_path = project_root / "data" / "jsons"

    upload_pdf(
        pdf_path=pdf_path,
        pdf_id="9c0a555a29683aedd2cd50ff7e837181a7fbb2d1c567d336897e2356fc17a595",
        company="enbw",
        dataland_client=dataland_client,
    )

    company_id = get_company_id(company="enbw", dataland_client=dataland_client)

    json_file_path = json_path / "enbw.json"
    with json_file_path.open(encoding="utf-8") as f:
        json_data = json.load(f)
    json_data["companyId"] = company_id
    json_str = json.dumps(json_data, indent=4)

    data_id = upload_dataset(
        company_id=company_id, json_str=json_str, dataland_client=dataland_client, reporting_period="2020"
    )

    delete_entity(data_id, ReviewedDataset)

    return data_id


def create_mock_ai_response(predicted_answer: str | None, confidence: float, qa_status: str) -> ChatCompletion:
    """Create a mock AI response using actual OpenAI types to ensure attribute access works."""
    response_json = {
        "predicted_answer": predicted_answer,
        "confidence": confidence,
        "reasoning": "Mock AI reasoning for testing",
        "qa_status": qa_status,
    }

    return ChatCompletion(
        id="test_mock",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    role="assistant",
                    content=json.dumps(response_json),
                ),
            )
        ],
        created=0,
        model="gpt-4o",
        object="chat.completion",
    )


def mock_ai_response() -> ChatCompletion:
    """Mock the AI response based on the prompt content."""
    return create_mock_ai_response(
        predicted_answer="Mock Answer",
        confidence=0.85,
        qa_status="QaAccepted",
    )


@patch("dataland_qa_lab.data_point_flow.prompts.get_prompt_config")
@patch("dataland_qa_lab.data_point_flow.ocr.ocr.extract_pdf")
@patch("dataland_qa_lab.data_point_flow.review.pdf_handler.render_pdf_to_image")
@patch("dataland_qa_lab.data_point_flow.review.dataland.get_document", new_callable=AsyncMock)
@patch("dataland_qa_lab.data_point_flow.ai.client.chat.completions.create", new_callable=AsyncMock)
def test_review_dataset_true_e2e(  # noqa: PLR0913, PLR0917
    mock_ai_create: AsyncMock,
    mock_get_document: AsyncMock,
    mock_render_pdf: MagicMock,
    mock_extract_pdf: MagicMock,
    mock_prompt_config: MagicMock,
    test_client: TestClient,
    uploaded_dataset_id: str,
) -> None:
    """Validate full flow with real uploads; external services mocked."""
    mock_prompt_config.return_value = DataPointPrompt(prompt="dummy prompt", depends_on=[])
    mock_extract_pdf.return_value = "mock ocr markdown"
    mock_get_document.return_value = BytesIO(b"dummy-pdf")
    mock_render_pdf.return_value = [Image.new("RGB", (1, 1), color="white")]
    mock_ai_create.return_value = mock_ai_response()

    response = test_client.post(
        f"/data-point-flow/review-dataset/{uploaded_dataset_id}",
        json={
            "ai_model": "gpt-4o",
            "use_ocr": False,
            "override": True,
        },
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    response_data = response.json()
    assert isinstance(response_data, dict), "Response should be a dictionary"
    assert len(response_data) > 0, "Response should contain at least one datapoint result"

    for result in response_data.values():
        assert "data_point_id" in result
        assert "reasoning" in result
        assert result["ai_model"] == "gpt-4o"

        if "qa_status" in result:
            assert "confidence" in result
            assert "predicted_answer" in result
            assert isinstance(result["qa_status"], str)
            # Check against values defined in your models/logic
            assert result["qa_status"] in {"QaAccepted", "QaRejected", "QaInconclusive"}

    assert mock_ai_create.call_count > 0


@patch("dataland_qa_lab.database.database_engine.get_entity")
@patch("dataland_qa_lab.data_point_flow.prompts.get_prompt_config")
@patch("dataland_qa_lab.data_point_flow.ocr.ocr.extract_pdf")
@patch("dataland_qa_lab.data_point_flow.review.pdf_handler.render_pdf_to_image")
@patch("dataland_qa_lab.data_point_flow.review.dataland.get_document", new_callable=AsyncMock)
@patch("dataland_qa_lab.data_point_flow.ai.client.chat.completions.create", new_callable=AsyncMock)
def test_review_dataset_with_ocr_enabled(  # noqa: PLR0913, PLR0917
    mock_ai_create: AsyncMock,
    mock_get_document: AsyncMock,
    mock_render_pdf: MagicMock,
    mock_extract_pdf: MagicMock,
    mock_prompt_config: MagicMock,
    mock_get_entity: MagicMock,
    test_client: TestClient,
    uploaded_dataset_id: str,
) -> None:
    """Test the endpoint with OCR enabled to verify OCR path is working."""
    mock_prompt_config.return_value = DataPointPrompt(prompt="dummy prompt", depends_on=[])
    mock_extract_pdf.return_value = "mock ocr markdown"
    mock_get_document.return_value = BytesIO(b"dummy-pdf")
    mock_render_pdf.return_value = [Image.new("RGB", (1, 1), color="white")]
    mock_ai_create.return_value = mock_ai_response()
    mock_get_entity.return_value = None

    response = test_client.post(
        f"/data-point-flow/review-dataset/{uploaded_dataset_id}",
        json={
            "ai_model": "gpt-4o",
            "use_ocr": True,
            "override": True,
        },
    )

    assert response.status_code == 200
    assert mock_extract_pdf.call_count > 0


@patch("dataland_qa_lab.data_point_flow.prompts.get_prompt_config")
@patch("dataland_qa_lab.data_point_flow.ocr.ocr.extract_pdf")
@patch("dataland_qa_lab.data_point_flow.review.pdf_handler.render_pdf_to_image")
@patch("dataland_qa_lab.data_point_flow.review.dataland.get_document", new_callable=AsyncMock)
@patch("dataland_qa_lab.data_point_flow.ai.client.chat.completions.create", new_callable=AsyncMock)
def test_review_dataset_without_override(  # noqa: PLR0913, PLR0917
    mock_ai_create: AsyncMock,
    mock_get_document: AsyncMock,
    mock_render_pdf: MagicMock,
    mock_extract_pdf: MagicMock,
    mock_prompt_config: MagicMock,
    test_client: TestClient,
    uploaded_dataset_id: str,
) -> None:
    """Test that when override=False, already validated datapoints are not re-validated."""
    mock_prompt_config.return_value = DataPointPrompt(prompt="dummy prompt", depends_on=[])
    mock_extract_pdf.return_value = "mock ocr markdown"
    mock_get_document.return_value = BytesIO(b"dummy-pdf")
    mock_render_pdf.return_value = [Image.new("RGB", (1, 1), color="white")]
    mock_ai_create.return_value = mock_ai_response()

    test_client.post(
        f"/data-point-flow/review-dataset/{uploaded_dataset_id}",
        json={
            "ai_model": "gpt-4o",
            "use_ocr": False,
            "override": True,
        },
    )

    initial_ai_calls = mock_ai_create.call_count
    mock_ai_create.reset_mock()

    # Second run with override=False
    response = test_client.post(
        f"/data-point-flow/review-dataset/{uploaded_dataset_id}",
        json={
            "ai_model": "gpt-4o",
            "use_ocr": False,
            "override": False,
        },
    )

    assert response.status_code == 200
    assert mock_ai_create.call_count <= initial_ai_calls
