import time

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CachedDocument(Base):
    """Database entity for cached documents."""

    __tablename__ = "cached_documents"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    file_name = Column("file_name", String, nullable=False)
    file_reference = Column("file_reference", String, nullable=False)
    ocr_output = Column("ocr_output", String, nullable=False)
    page = Column("page", Integer, nullable=False)

    timestamp = Column("timestamp", Integer, default=int(time.time()), nullable=False)
