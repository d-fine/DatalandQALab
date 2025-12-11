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
    timestamp: int
    ai_model: str
    use_ocr: bool
    override: bool
    file_name: str
    file_reference: str
    page: int


@dataclass
class CannotValidateDatapoint:
    """Structure to indicate a datapoint cannot be validated."""

    data_point_id: str
    data_point_type: str | None
    reasoning: str
    ai_model: str
    use_ocr: bool
    override: bool
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


@dataclass
class DataPointPrompt:
    prompt: str
    depends_on: list[str]


@dataclass
class AIResponse:
    predicted_answer: str | None
    confidence: float
    reasoning: str
