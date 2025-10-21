import logging

from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from dataland_qa_lab.database.database_tables import Base
from dataland_qa_lab.utils import config

DATABASE_URL = config.get_config().database_connection_string

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

logger = logging.getLogger(__name__)


def create_tables() -> None:
    """Create all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Creating tables in database")
    except Exception as e:
        logger.exception(msg="Error while creating tables in database", exc_info=e)
        return False
    return True


def add_entity(entity: any) -> bool:
    """Generic method to add an entity to the database."""
    session = SessionLocal()

    try:
        session.add(entity)
        session.commit()
    except SQLAlchemyError:
        logger.exception(msg="Error while adding entity to database", exc_info=SQLAlchemyError)
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
        logger.exception(msg="Error retrieving entity", exc_info=SQLAlchemyError)
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
        logger.exception(msg="Error updating entity", exc_info=SQLAlchemyError)
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
        else:
            logger.error(msg="Entity not found")
            return False
        session.commit()
    except SQLAlchemyError:
        logger.exception(msg="Error updating entity", exc_info=SQLAlchemyError)
        session.rollback()
        return False
    finally:
        session.close()

    return True
