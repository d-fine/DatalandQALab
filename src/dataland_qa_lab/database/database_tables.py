import time
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Integer, String
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


class ReviewedDatasetMarkdowns(Base):
    """Caching the Markdowns of the company reports."""

    __tablename__ = "reviewed_dataset_markdowns"
    data_id = Column("data_id", String, primary_key=True)
    page_numbers = Column("page_numbers", ARRAY(Integer), nullable=True)
    last_saved = Column("last_saved", DateTime, default=datetime.utcnow)
    last_updated = Column("last_updated", DateTime, default=datetime.utcnow)
    markdown_text = Column("markdown_text", String, nullable=False)


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
    qa_status = Column("qa_status", String, nullable=False)
    timestamp = Column("timestamp", Integer, default=int(time.time()), nullable=False)
