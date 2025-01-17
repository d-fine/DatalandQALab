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
