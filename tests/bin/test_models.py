import pytest
from pydantic import ValidationError

from dataland_qa_lab.bin.models import (
    DatapointFlowReviewDataPointRequest,
    ReviewMeta,
    ReviewRequest,
    ReviewResponse,
)


def test_review_request_defaults() -> None:
    """Test default values of ReviewRequest model."""
    model = ReviewRequest()
    assert model.force_review is False
    assert model.ai_model == "gpt-5"
    assert model.use_ocr is True


def test_review_meta_valid() -> None:
    """Test valid ReviewMeta model."""
    meta = ReviewMeta(
        timestamp="2025-01-01T00:00:00Z",
        ai_model="gpt-5",
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
            ai_model="gpt-5",
            force_review=False,
            use_ocr=True,
        )


def test_review_response_valid() -> None:
    """Test valid ReviewResponse model."""
    meta = ReviewMeta(
        timestamp="2025-01-01T00:00:00Z",
        ai_model="gpt-5",
        force_review=False,
        use_ocr=True,
    )
    resp = ReviewResponse(
        data={"result": "ok"},
        meta=meta,
    )
    assert resp.data["result"] == "ok"
    assert resp.meta.ai_model == "gpt-5"


def test_datapoint_flow_request_defaults() -> None:
    """Test default values of DatapointFlowReviewDataPointRequest model."""
    req = DatapointFlowReviewDataPointRequest()
    assert req.ai_model == "gpt-5"
    assert req.use_ocr is True
    assert req.override is False
