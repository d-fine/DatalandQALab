from typing import Any

from pydantic import BaseModel


class ReviewRequest(BaseModel):
    """Request body for the /review/{data_id} POST endpoint."""

    ai_model: str = "gpt-4o"
    force_review: bool = False
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
