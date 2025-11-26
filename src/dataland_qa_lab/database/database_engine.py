import logging
import sys
from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from dataland_qa_lab.database.database_tables import Base
from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)

DATABASE_URL = config.get_config().database_connection_string

# Create engine once
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


def add_entity(entity: Any) -> bool:
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


def get_entity(entity_id: str, entity_class: type[Any]) -> Any | None:
    """Generic method to get an entity from the database by its ID."""
    session = SessionLocal()
    entity = None

    try:
        primary_key_column = inspect(entity_class).primary_key[0]
        entity = session.query(entity_class).filter(primary_key_column == entity_id).first()
    except SQLAlchemyError as e:
        logger.exception(msg="Error retrieving entity", exc_info=e)
    finally:
        session.close()

    return entity


def update_entity(entity: Any) -> bool:
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
