import time
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ReviewedDataset(Base):
    """Database entity review_dataset."""

    __tablename__ = "reviewed_dataset"
    data_id = Column("data_id", String, primary_key=True)
    review_start_time = Column("review_start_time", String, nullable=False)
    review_end_time = Column("review_end_time", String, nullable=True)
    review_completed = Column("review_completed", Boolean, nullable=True, default=False)
    report_id = Column("report_id", String, nullable=True)
    error_reason = Column("error_reason", String, nullable=True)


class ReviewedDatasetMarkdowns(Base):
    """Caching the Markdowns of the company reports."""

    __tablename__ = "reviewed_dataset_markdowns"
    data_id = Column("data_id", String, primary_key=True)
    page_numbers = Column("page_numbers", ARRAY(Integer), nullable=True)
    last_saved = Column("last_saved", DateTime, default=datetime.utcnow)
    last_updated = Column("last_updated", DateTime, default=datetime.utcnow)
    markdown_text = Column("markdown_text", String, nullable=False)
    llm_version = Column("llm_version", String, nullable=True)


class CachedDocument(Base):
    """Database entity for cached documents."""

    __tablename__ = "cached_documents"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    file_name = Column("file_name", String, nullable=False)
    file_reference = Column("file_reference", String, nullable=False)
    ocr_output = Column("ocr_output", String, nullable=False)
    page = Column("page", Integer, nullable=False)

    timestamp = Column("timestamp", Integer, default=int(time.time()), nullable=False)


class ValidatedDataPoint(Base):
    """Database entity for validated data points."""

    __tablename__ = "validated_data_point"
    data_point_id = Column("data_point_id", String, primary_key=True)
    data_point_type = Column("data_point_type", String, nullable=True)
    previous_answer = Column("previous_answer", String, nullable=True)
    predicted_answer = Column("predicted_answer", String, nullable=True)
    confidence = Column("confidence", Float, nullable=True)
    reasoning = Column("reasoning", String, nullable=True)
    qa_status = Column("qa_status", String, nullable=True)
    timestamp = Column("timestamp", Integer, default=int(time.time()), nullable=True)
    ai_model = Column("ai_model", String, nullable=True)
    use_ocr = Column("use_ocr", Boolean, nullable=True)
    override = Column("override", Boolean, nullable=True)
    file_name = Column("file_name", String, nullable=True)
    file_reference = Column("file_reference", String, nullable=True)
    page = Column("page", Integer, nullable=True)
    qa_report_id = Column("qa_report_id", String, nullable=True)
    _prompt = Column("_prompt", String, nullable=True)


class DatapointInReview(Base):
    """Database entity for datapoints currently in review."""

    __tablename__ = "datapoint_in_review"
    data_point_id = Column("data_point_id", String, primary_key=True)
    locked_at = Column("locked_at", Integer, default=lambda: int(time.time()), nullable=False)
