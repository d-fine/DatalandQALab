import pytest
from pydantic import ValidationError

from dataland_qa_lab.bin.models import ReviewMeta, ReviewRequest, ReviewResponse


def test_review_request_defaults() -> None:
    """Test that default values are set correctly in ReviewRequest."""
    req = ReviewRequest()

    assert req.ai_model == "gpt-4o"
    assert req.force_review is False
    assert req.use_ocr is True


def test_review_request_override_fields() -> None:
    """Test that fields can be overridden in ReviewRequest."""
    req = ReviewRequest(ai_model="custom-model", force_review=True, use_ocr=False)

    assert req.ai_model == "custom-model"
    assert req.force_review is True
    assert req.use_ocr is False


def test_review_request_invalid_field_type() -> None:
    """Test that invalid field types raise ValidationError in ReviewRequest."""
    with pytest.raises(ValidationError):
        ReviewRequest(force_review="not-a-bool")  # type: ignore


def test_review_meta_valid() -> None:
    """Test that ReviewMeta accepts valid data."""
    meta = ReviewMeta(timestamp="2025-01-01T10:00:00Z", ai_model="gpt-4o", force_review=True, use_ocr=False)

    assert meta.timestamp == "2025-01-01T10:00:00Z"
    assert meta.ai_model == "gpt-4o"
    assert meta.force_review is True
    assert meta.use_ocr is False


def test_review_meta_missing_field() -> None:
    """Test that missing fields raise ValidationError in ReviewMeta."""
    with pytest.raises(ValidationError):
        ReviewMeta(ai_model="gpt-4o", force_review=True, use_ocr=False)  # type: ignore


def test_review_meta_invalid_type() -> None:
    """Test that invalid field types raise ValidationError in ReviewMeta."""
    with pytest.raises(ValidationError):
        ReviewMeta(
            timestamp=123,
            ai_model="gpt-4o",
            force_review=False,
            use_ocr=True,
        )


def test_review_response_valid() -> None:
    """Test that ReviewResponse accepts valid data."""
    meta = ReviewMeta(
        timestamp="2025-01-01T10:00:00Z",
        ai_model="gpt-4o",
        force_review=False,
        use_ocr=True,
    )

    resp = ReviewResponse(data={"a": 1, "b": "ok"}, meta=meta)

    assert resp.data == {"a": 1, "b": "ok"}
    assert resp.meta == meta


def test_review_response_meta_as_dict() -> None:
    """Pydantic should auto-convert dict to ReviewMeta."""
    resp = ReviewResponse(
        data={"value": 42},
        meta={
            "timestamp": "2025-10-10T10:00:00Z",
            "ai_model": "gpt-4o",
            "force_review": True,
            "use_ocr": False,
        },  # type: ignore
    )

    assert resp.meta.timestamp == "2025-10-10T10:00:00Z"
    assert resp.meta.force_review is True
    assert isinstance(resp.meta, ReviewMeta)


def test_review_response_invalid_data_type() -> None:
    """Test that invalid data types raise ValidationError in ReviewResponse."""
    with pytest.raises(ValidationError):
        ReviewResponse(
            data="not-a-dict",  # type: ignore
            meta={"timestamp": "2025-10-10", "ai_model": "gpt-4o", "force_review": False, "use_ocr": True},  # type: ignore
        )
