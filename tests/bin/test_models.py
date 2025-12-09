import pytest
from pydantic import ValidationError

from dataland_qa_lab.bin.models import (
    DatapointFlowCannotReviewDatapointResponse,
    DatapointFlowReviewDataPointRequest,
    DatapointFlowReviewDataPointResponse,
    DatapointFlowReviewDatasetResponse,
    ReviewMeta,
    ReviewRequest,
    ReviewResponse,
)


def test_review_request_defaults() -> None:
    """Test default values of ReviewRequest model."""
    model = ReviewRequest()
    assert model.force_review is False
    assert model.ai_model == "gpt-4o"
    assert model.use_ocr is True


def test_review_meta_valid() -> None:
    """Test valid ReviewMeta model."""
    meta = ReviewMeta(
        timestamp="2025-01-01T00:00:00Z",
        ai_model="gpt-4o",
        force_review=True,
        use_ocr=False,
    )
    assert meta.timestamp == "2025-01-01T00:00:00Z"
    assert meta.force_review is True
    assert meta.use_ocr is False


def test_review_meta_invalid_missing_field() -> None:
    """Test invalid ReviewMeta model with missing field."""
    with pytest.raises(ValidationError):
        ReviewMeta(
            ai_model="gpt-4o",
            force_review=False,
            use_ocr=True,
        )


def test_review_response_valid() -> None:
    """Test valid ReviewResponse model."""
    meta = ReviewMeta(
        timestamp="2025-01-01T00:00:00Z",
        ai_model="gpt-4o",
        force_review=False,
        use_ocr=True,
    )
    resp = ReviewResponse(
        data={"result": "ok"},
        meta=meta,
    )
    assert resp.data["result"] == "ok"
    assert resp.meta.ai_model == "gpt-4o"


def test_datapoint_flow_request_defaults() -> None:
    """Test default values of DatapointFlowReviewDataPointRequest model."""
    req = DatapointFlowReviewDataPointRequest()
    assert req.ai_model == "gpt-4o"
    assert req.use_ocr is True
    assert req.override is False


def test_datapoint_flow_review_datapoint_response_valid() -> None:
    """Test valid DatapointFlowReviewDataPointResponse model."""
    resp = DatapointFlowReviewDataPointResponse(
        data_point_id="123",
        data_point_type="invoice",
        previous_answer="OLD",
        predicted_answer="NEW",
        confidence=0.92,
        reasoning="High confidence based on OCR.",
        qa_status="reviewed",
        timestamp=1735689600,
        ai_model="gpt-4o",
        use_ocr=True,
        file_name="file.pdf",
        file_reference="ref_001",
        page=1,
    )
    assert resp.status == "success"
    assert resp.confidence == 0.92
    assert resp.page == 1


def test_datapoint_flow_review_datapoint_response_invalid_confidence() -> None:
    """Test invalid DatapointFlowReviewDataPointResponse model with wrong confidence type."""
    with pytest.raises(ValidationError):
        DatapointFlowReviewDataPointResponse(
            data_point_id="123",
            data_point_type="invoice",
            previous_answer="OLD",
            predicted_answer="NEW",
            confidence="high",
            reasoning="Invalid confidence type.",
            qa_status="reviewed",
            timestamp=1735689600,
            ai_model="gpt-4o",
            use_ocr=True,
            file_name="file.pdf",
            file_reference="ref",
            page=1,
        )


def test_datapoint_flow_cannot_review_response_valid() -> None:
    """Test valid DatapointFlowCannotReviewDatapointResponse model."""
    resp = DatapointFlowCannotReviewDatapointResponse(
        data_point_id="99",
        data_point_type="unsupported",
        reasoning="Unsupported file format",
        ai_model="gpt-4o",
        use_ocr=False,
        timestamp=1735689600,
    )
    assert resp.status == "error"
    assert resp.reasoning == "Unsupported file format"
    assert resp.use_ocr is False


def test_datapoint_flow_cannot_review_response_missing_field() -> None:
    """Test invalid DatapointFlowCannotReviewDatapointResponse model with missing field."""
    with pytest.raises(ValidationError):
        DatapointFlowCannotReviewDatapointResponse(
            data_point_type="invoice",
            reasoning="Missing ID",
            ai_model="gpt-4o",
            use_ocr=True,
            timestamp=1735689600,
        )


def test_dataset_response_mixed_entries() -> None:
    """Test DatapointFlowReviewDatasetResponse with mixed valid and error entries."""
    valid_resp = DatapointFlowReviewDataPointResponse(
        data_point_id="123",
        data_point_type="invoice",
        previous_answer="A",
        predicted_answer="B",
        confidence=0.8,
        reasoning="OK",
        qa_status="reviewed",
        timestamp=1735689600,
        ai_model="gpt-4o",
        use_ocr=True,
        file_name="file.pdf",
        file_reference="ref",
        page=2,
    )

    error_resp = DatapointFlowCannotReviewDatapointResponse(
        data_point_id="999",
        data_point_type="unknown",
        reasoning="Corrupt file",
        ai_model="gpt-4o",
        use_ocr=False,
        timestamp=1735689600,
    )

    dataset = DatapointFlowReviewDatasetResponse(
        data_points={
            "item_1": valid_resp,
            "item_2": error_resp,
        }
    )

    assert dataset.data_points["item_1"].status == "success"
    assert dataset.data_points["item_2"].status == "error"
    assert len(dataset.data_points) == 2


def test_dataset_response_invalid_value_type() -> None:
    """Test invalid DatapointFlowReviewDatasetResponse with invalid value type."""
    with pytest.raises(ValidationError):
        DatapointFlowReviewDatasetResponse(data_points={"invalid": {"not": "a model instance"}})
