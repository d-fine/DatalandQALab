from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
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
    markdown_text = Column("markdown_text", String, nullable=False)
    relevant_pages_pdf_reader = Column("relevant_pages_pdf_reader", String, nullable=True)
    last_saved = Column("last_saved", DateTime, default=datetime.utcnow)
    last_updated = Column("last_updated", DateTime, default=datetime.utcnow)
