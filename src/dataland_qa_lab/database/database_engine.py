import logging
import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from dataland_qa_lab.database.database_tables import Base

DATABASE_URL = os.getenv("DATABASE_CONNECTION_STRING")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

logger = logging.getLogger(__name__)


def create_tables() -> None:
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def add_entity(entity: any) -> bool:
    """Generic method to add an entity to the database."""
    session = SessionLocal()

    try:
        session.add(entity)
        session.commit()
    except SQLAlchemyError:
        logger.exception("Error while adding entity to database")
        session.rollback()
        return False
    finally:
        session.close()

    return True


def get_entity(entity_id: str, entity_class: any) -> any:
    """Generic method to get an entity from the database by its ID."""
    session = SessionLocal()

    try:
        primary_key_column = inspect(entity_class).primary_key[0]
        entity = session.query(entity_class).filter(primary_key_column == entity_id).first()
        session.commit()
    except SQLAlchemyError:
        logger.exception("Error retrieving entity")
        session.rollback()
        return None
    finally:
        session.close()

    return entity


def update_entity(entity: any) -> bool:
    """Generic method to update an entity in the database."""
    session = SessionLocal()

    try:
        session.merge(entity)
        session.commit()
    except SQLAlchemyError:
        logger.exception("Error updating entity")
        session.close()
        return False
    finally:
        session.close()

    return True


def delete_entity(entity_id: str, entity_class: any) -> bool:
    """Generic method to delete an entity from the database by its ID."""
    session = SessionLocal()

    try:
        primary_key_column = inspect(entity_class).primary_key[0]
        entity = session.query(entity_class).filter(primary_key_column == entity_id).first()
        if entity:
            session.delete(entity)
            session.commit()
        else:
            logger.error("Entity not found")
            return False
        session.commit()
    except SQLAlchemyError:
        logger.exception("Error updating entity")
        session.rollback()
        return False
    finally:
        session.close()

    return True
