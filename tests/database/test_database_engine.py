from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from dataland_qa_lab.database import database_engine


@pytest.fixture
def mock_session() -> MagicMock:
    # Mock session object
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def patch_session(mock_session: MagicMock) -> MagicMock:
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
@patch("dataland_qa_lab.database.database_engine.inspect")
def test_get_entity(mock_inspect: MagicMock, mock_session_local: MagicMock) -> None:
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    mock_entity_class = MagicMock()
    mock_entity_instance = MagicMock()

    mock_primary_key = MagicMock()
    mock_inspect.return_value.primary_key = [mock_primary_key]

    mock_query = mock_session.query.return_value
    mock_query.filter.return_value.first.return_value = mock_entity_instance

    result = database_engine.get_entity("1", mock_entity_class)

    mock_session.query.assert_called_once_with(mock_entity_class)
    mock_query.filter.assert_called_once_with(mock_primary_key == "1")
    mock_session.close.assert_called_once()
    assert result == mock_entity_instance


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


@patch("dataland_qa_lab.database.database_engine.SessionLocal")
def test_sqlalchemy_errors(mock_session_local: MagicMock) -> None:
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    mock_entity = MagicMock()
    mock_session.add.side_effect = SQLAlchemyError("DB Error")
    result = database_engine.add_entity(mock_entity)

    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
    assert result is False


@patch("dataland_qa_lab.database.database_engine.SessionLocal")
def test_add_entity_database_error(mock_session_local: MagicMock) -> None:
    """Test entity addition with database error."""
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    mock_entity = MagicMock()
    mock_session.add.side_effect = SQLAlchemyError("DB Error")

    result = database_engine.add_entity(mock_entity)

    assert result is False
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()


@patch("dataland_qa_lab.database.database_engine.SessionLocal")
@patch("dataland_qa_lab.database.database_engine.inspect")
def test_get_entity_database_error(mock_inspect: MagicMock, mock_session_local: MagicMock) -> None:
    """Test entity retrieval with database error."""
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    mock_entity_class = MagicMock()

    mock_primary_key = MagicMock()
    mock_inspect.return_value.primary_key = [mock_primary_key]

    mock_session.query.side_effect = SQLAlchemyError("DB Error")

    result = database_engine.get_entity("123", mock_entity_class)

    assert result is None
    mock_session.close.assert_called_once()


@patch("dataland_qa_lab.database.database_engine.SessionLocal")
def test_update_entity_database_error(mock_session_local: MagicMock) -> None:
    """Test entity update with database error."""
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    mock_entity = MagicMock()
    mock_session.merge.side_effect = SQLAlchemyError("DB Error")

    result = database_engine.update_entity(mock_entity)

    assert result is False
    mock_session.close.assert_called_once()


@patch("dataland_qa_lab.database.database_engine.SessionLocal")
@patch("dataland_qa_lab.database.database_engine.inspect")
def test_delete_entity_not_found(mock_inspect: MagicMock, mock_session_local: MagicMock) -> None:
    """Test entity deletion when entity not found."""
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    mock_entity_class = MagicMock()

    mock_primary_key = MagicMock()
    mock_inspect.return_value.primary_key = [mock_primary_key]

    mock_query = mock_session.query.return_value
    mock_query.filter.return_value.first.return_value = None

    result = database_engine.delete_entity("999", mock_entity_class)

    assert result is False
    mock_session.close.assert_called_once()


@patch("dataland_qa_lab.database.database_engine.SessionLocal")
@patch("dataland_qa_lab.database.database_engine.inspect")
def test_delete_entity_database_error(mock_inspect: MagicMock, mock_session_local: MagicMock) -> None:
    """Test entity deletion with database error."""
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    mock_entity_class = MagicMock()

    mock_primary_key = MagicMock()
    mock_inspect.return_value.primary_key = [mock_primary_key]

    mock_session.query.side_effect = SQLAlchemyError("DB Error")

    result = database_engine.delete_entity("123", mock_entity_class)

    assert result is False
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
