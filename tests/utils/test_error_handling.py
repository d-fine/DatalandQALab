import pytest

from dataland_qa_lab.utils.error_handling import NetworkError, UnknownError


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
