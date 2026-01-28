import logging
import sys
import time
from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from dataland_qa_lab.database.database_tables import Base
from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)

DATABASE_URL = config.get_config().database_connection_string

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def verify_database_connection() -> None:
    """Verify the database connection. If failed, log critical error and exit."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Database connection verified successfully.")
    except SQLAlchemyError as e:
        logger.critical("Database connection failed. Exiting application.", exc_info=e)
        sys.exit(1)


def create_tables() -> bool:
    """Create all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Creating tables in database")
    except Exception as e:
        logger.exception(msg="Error while creating tables in database", exc_info=e)
        return False
    return True


def add_entity(entity: Any) -> bool:  # noqa: ANN401
    """Generic method to add an entity to the database."""
    session = SessionLocal()

    try:
        session.add(entity)
        session.commit()
    except SQLAlchemyError as e:
        logger.exception(msg="Error while adding entity to database", exc_info=e)
        session.rollback()
        return False
    finally:
        session.close()

    return True


def get_entity(entity_class: Any, **filters) -> Any:  # noqa: ANN003, ANN401
    """Generic method to get an entity from the database by its ID."""
    session = SessionLocal()

    try:
        query = session.query(entity_class)
        for field, value in filters.items():
            query = query.filter(getattr(entity_class, field) == value)

        session.commit()
        return query.first()
    except SQLAlchemyError:
        session.rollback()
        return None
    finally:
        session.close()


def update_entity(entity: Any) -> bool:  # noqa: ANN401
    """Generic method to update an entity in the database."""
    session = SessionLocal()

    try:
        session.merge(entity)
        session.commit()
    except SQLAlchemyError as e:
        logger.exception(msg="Error updating entity", exc_info=e)
        return False
    finally:
        session.close()

    return True


def delete_entity(entity_id: str, entity_class: type[Any]) -> bool:
    """Generic method to delete an entity from the database by its ID."""
    session = SessionLocal()

    try:
        primary_key_column = inspect(entity_class).primary_key[0]
        entity = session.query(entity_class).filter(primary_key_column == entity_id).first()
        if entity:
            session.delete(entity)
            session.commit()
        else:
            logger.error(msg="Entity not found")
            return False
    except SQLAlchemyError as e:
        logger.exception(msg="Error deleting entity", exc_info=e)
        session.rollback()
        return False
    finally:
        session.close()

    return True


def acquire_or_refresh_datapoint_lock(data_point_id: str, lock_ttl_seconds: int) -> bool:
    """Acquire or refresh a lock for a data point (atomic upsert)."""
    session = SessionLocal()
    now_ts = int(time.time())
    stale_before = now_ts - lock_ttl_seconds

    try:
        result = session.execute(
            text(
                """
                INSERT INTO datapoint_in_review (data_point_id, locked_at)
                VALUES (:id, :now_ts)
                ON CONFLICT (data_point_id) DO UPDATE
                  SET locked_at = EXCLUDED.locked_at
                  WHERE datapoint_in_review.locked_at < :stale_before
                RETURNING data_point_id
                """
            ),
            {"id": data_point_id, "now_ts": now_ts, "stale_before": stale_before},
        )
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception("Error acquiring or refreshing datapoint lock", exc_info=e)
        return False
    else:
        return result.first() is not None
    finally:
        session.close()
