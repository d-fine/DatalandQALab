from typing import Any

from pydantic import BaseModel


class ReviewRequest(BaseModel):
    """Request model for initiating a review."""

    force_review: bool = False
    ai_model: str = "gpt-4o"
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


# models for the new dataset validation
class DatapointFlowReviewDataPointRequest(BaseModel):
    """Request model for initiating a data point review."""

    ai_model: str = "gpt-4o"
    use_ocr: bool = True
    override: bool = False


class DatapointFlowReviewDataPointResponse(BaseModel):
    """Response model for a reviewed data point."""

    data_point_id: str
    data_point_type: str
    previous_answer: Any
    predicted_answer: Any
    confidence: float
    reasoning: str
    qa_status: str
    timestamp: int
    ai_model: str
    use_ocr: bool
    file_name: str
    file_reference: str
    page: int
    status: str = "success"


class DatapointFlowCannotReviewDatapointResponse(BaseModel):
    """Response model for a data point that cannot be reviewed."""

    data_point_id: str
    data_point_type: str
    reasoning: str
    ai_model: str
    use_ocr: bool
    timestamp: int
    status: str = "error"


class DatapointFlowReviewDatasetResponse(BaseModel):
    """Response model for a dataset of reviewed data points."""

    data_points: dict[str, DatapointFlowReviewDataPointResponse | DatapointFlowCannotReviewDatapointResponse]
