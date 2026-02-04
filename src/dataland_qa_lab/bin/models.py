from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ReviewConfig(BaseModel):
    """Review configuration."""

    ai_model: str = "gpt-5"
    use_ocr: bool = True


class ReviewRequest(ReviewConfig):
    """Review request configuration."""

    force_review: bool = False


class ReviewMeta(ReviewConfig):
    """Review metadata."""

    timestamp: datetime = Field(default_factory=datetime.now)
    force_review: bool


class ReviewResponse(BaseModel):
    """Review response."""

    data: dict[str, Any]
    meta: ReviewMeta


class DatapointFlowReviewDataPointRequest(ReviewConfig):
    """Request model for initiating a data point review."""

    override: bool = False
