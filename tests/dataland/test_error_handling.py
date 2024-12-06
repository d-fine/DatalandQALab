import pytest

from dataland_qa_lab.dataland.error_handling import ErrorHandling, NetworkError, UnknownError


def test_network_error() -> None:
    """Test the NetworkError exception."""
    msg = "Connection timed out"
    with pytest.raises(NetworkError) as excinfo:
        raise NetworkError(msg)
    assert str(excinfo.value) == "Network error occurred: Connection timed out"
    assert excinfo.value.error == "Connection timed out"


def test_unknown_error() -> None:
    msg = "Unexpected failure"
    """Test the UnknownError exception."""
    with pytest.raises(UnknownError) as excinfo:
        raise UnknownError(msg)
    assert str(excinfo.value) == "Unknown error occurred: Unexpected failure"
    assert excinfo.value.error == "Unexpected failure"


@pytest.fixture
def error_handling_instance() -> ErrorHandling:
    """Fixture to provide a fresh instance of ErrorHandling."""
    return ErrorHandling()


def test_log_network_error(error_handling_instance: ErrorHandling) -> None:
    """Test logging and raising a network error."""
    msg = "Server unreachable"
    with pytest.raises(NetworkError) as excinfo:
        error_handling_instance.log_network_error(msg)
    assert "Server unreachable" in error_handling_instance.network_errors
    assert str(excinfo.value) == "Network error occurred: Server unreachable"
    assert excinfo.value.error == "Server unreachable"


def test_log_unknown_error(error_handling_instance: ErrorHandling) -> None:
    """Test logging and raising an unknown error."""
    with pytest.raises(UnknownError) as excinfo:
        error_handling_instance.log_unknown_error("Unexpected behavior")
    assert "Unexpected behavior" in error_handling_instance.unknown_errors
    assert str(excinfo.value) == "Unknown error occurred: Unexpected behavior"
    assert excinfo.value.error == "Unexpected behavior"


def test_error_handling_initialization() -> None:
    """Test the initialization of the ErrorHandling class."""
    handler = ErrorHandling()
    assert handler.network_errors == []
    assert handler.unknown_errors == []
