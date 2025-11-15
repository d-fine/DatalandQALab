from unittest.mock import Mock

from dataland_qa_lab.utils.sfdr_data_collection import SFDRDataCollection
from tests.utils.provide_sfdr_test_data_collection import provide_sfdr_test_data_collection


def test_get_scope1_ghg_emissions() -> None:
    """Test succesful extraction of Scope1 GHG emissions value."""
    collection = provide_sfdr_test_data_collection()
    assert collection.get_scope1_ghg_emissions() == 12345.67


def test_get_scope1_file_reference() -> None:
    """Test successful extraction of Scope1 GHG emissions file reference."""
    collection = provide_sfdr_test_data_collection()
    assert collection.get_scope1_file_reference() == "sfdr-test-file-ref"


def test_get_scope1_page_number() -> None:
    """Test successful extraction of Scope1 GHG emissions page number."""
    collection = provide_sfdr_test_data_collection()
    assert collection.get_scope1_page_number() == "45"


def test_get_scope1_ghg_emissions_no_data() -> None:
    """Test behaviour when data is missing."""
    empty_data = Mock()

    del empty_data.environmental
    collection = SFDRDataCollection(empty_data)
    assert collection.get_scope1_ghg_emissions() is None
