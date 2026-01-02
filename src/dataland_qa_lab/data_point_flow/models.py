from dataclasses import dataclass
from typing import Any


@dataclass
class ValidatedDatapoint:
    """Structure to hold validated datapoint information."""

    data_point_id: str
    data_point_type: str
    previous_answer: str | None
    predicted_answer: str | None
    confidence: float
    reasoning: str
    qa_status: str
    ai_model: str
    use_ocr: bool
    override: bool | None
    file_name: str
    file_reference: str
    page: int
    _prompt: str | None
    timestamp: int


@dataclass
class CannotValidateDatapoint:
    """Structure to indicate a datapoint cannot be validated."""

    data_point_id: str
    data_point_type: str | None
    reasoning: str
    ai_model: str
    use_ocr: bool
    override: bool | None
    _prompt: str | None
    timestamp: int


@dataclass
class DataPoint:
    """Structure to hold basic datapoint information."""

    data_point_id: str
    data_point_type: str
    data_source: dict[str, Any]
    page: int
    file_reference: str
    file_name: str
    value: str
    comment: str
    quality: str
    _all: dict[str, Any]


@dataclass
class DataPointPrompt:
    """Data structure for data point prompts."""

    prompt: str
    depends_on: list[str]


@dataclass
class AIResponse:
    """Data structure for AI model responses."""

    predicted_answer: str | None
    confidence: float
    reasoning: str
    qa_status: str
