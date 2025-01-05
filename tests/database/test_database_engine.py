from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from dataland_qa_lab.database import database_engine


@pytest.fixture
def mock_session() -> MagicMock:
    # Mock session object
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def patch_session(mock_session: MagicMock) -> MagicMock:
    # Patch the sessionmaker to return the mock session
    with patch("dataland_qa_lab.database.database_engine.SessionLocal", return_value=mock_session):
        return


@patch("dataland_qa_lab.database.database_engine.Base.metadata.create_all")
def test_create_tables(mock_create_all: MagicMock) -> None:
    """Test to ensure creating tables works as intended."""
    database_engine.create_tables()
    mock_create_all.assert_called_once_with(bind=database_engine.engine)


@patch("dataland_qa_lab.database.database_engine.SessionLocal")
def test_add_entity(mock_session_local: MagicMock) -> None:
    """Test to ensure adding an entity works as intended."""
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    mock_entity = MagicMock()
    result = database_engine.add_entity(mock_entity)

    mock_session.add.assert_called_once_with(mock_entity)
    mock_session.commit.assert_called_once()
    assert result is True


@patch("dataland_qa_lab.database.database_engine.SessionLocal")
def test_get_entity(mock_session_local: MagicMock) -> None:
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    mock_entity_class = MagicMock()
    mock_entity = MagicMock()
    mock_query = mock_session.query.return_value
    mock_query.filter.return_value.first.return_value = mock_entity

    result = database_engine.get_entity("1", mock_entity_class)

    mock_session.query.assert_called_once_with(mock_entity_class)
    mock_query.filter.assert_called_once()
    assert result == mock_entity


@patch("dataland_qa_lab.database.database_engine.SessionLocal")
def test_update_entity(mock_session_local: MagicMock) -> None:
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    mock_entity = MagicMock()
    result = database_engine.update_entity(mock_entity)

    mock_session.merge.assert_called_once_with(mock_entity)
    mock_session.commit.assert_called_once()
    assert result is True


@patch("dataland_qa_lab.database.database_engine.SessionLocal")
def test_delete_entity(mock_session_local: MagicMock) -> None:
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    mock_entity_class = MagicMock()
    mock_entity = MagicMock()
    mock_query = mock_session.query.return_value
    mock_query.filter.return_value.first.return_value = mock_entity

    result = database_engine.delete_entity(1, mock_entity_class)

    mock_session.query.assert_called_once_with(mock_entity_class)
    mock_query.filter.assert_called_once()
    mock_session.delete.assert_called_once_with(mock_entity)
    mock_session.commit.assert_called_once()
    assert result is True
