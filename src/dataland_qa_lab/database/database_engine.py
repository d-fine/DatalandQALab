import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dataland_qa_lab.database.database_tables import Base

DATABASE_URL = os.getenv("DATABASE_CONNECTION_STRING")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


def create_tables() -> None:
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def add_entity(entity: any) -> bool:
    """Generic method to add an entity to the database."""
    session = SessionLocal()

    try:
        session.add(entity)
    except Exception as e:
        # log error
        session.close()
        return False

    session.commit()
    session.close()
    return True


def get_entity(entity_id: str, entity_class: any) -> any:
    """Generic method to get an entity from the database by its ID."""
    session = SessionLocal()

    try:
        entity = session.query(entity_class).filter(entity_class.data_id == entity_id).first()
    except Exception as e:
        # log error
        print(f"Error retrieving entity with id {entity_id}: {e}")
        session.close()
        return None

    session.close()
    return entity


def update_entity(entity: any) -> bool:
    """Generic method to update an entity in the database."""
    session = SessionLocal()

    try:
        session.merge(entity)
    except Exception as e:
        # log error
        print(f"Error updating entity: {e}")
        session.close()
        return False

    session.commit()
    session.close()
    return True


def delete_entity(entity_id: int, entity_class: any) -> bool:
    """Generic method to delete an entity from the database by its ID."""
    session = SessionLocal()

    try:
        entity = session.query(entity_class).filter(entity_class.data_id == entity_id).first()
        if entity:
            session.delete(entity)
        else:
            print("Entity not found.")
            return False
    except Exception as e:
        # log error
        print(f"Error deleting entity: {e}")
        session.close()
        return False

    session.commit()
    session.close()
    return True
