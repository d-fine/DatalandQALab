from typing import Any

from pydantic import BaseModel


class ReviewRequest(BaseModel):
    """Request model for initiating a review."""

    force_review: bool = False
    ai_model: str = "gpt-5"
    use_ocr: bool = True


class ReviewMeta(BaseModel):
    """Metadata about the review request and processing."""

    timestamp: str
    ai_model: str
    force_review: bool
    use_ocr: bool


class ReviewResponse(BaseModel):
    """Response wrapper containing data and metadata."""

    data: dict[str, Any]
    meta: ReviewMeta


class DatapointFlowReviewDataPointRequest(BaseModel):
    """Request model for initiating a data point review."""

    ai_model: str = "gpt-5"
    use_ocr: bool = True
    override: bool = False
