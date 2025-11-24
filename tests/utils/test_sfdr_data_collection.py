from unittest.mock import Mock

import pytest

from dataland_qa_lab.utils.sfdr_data_collection import SFDRDataCollection


class TestSFDRDataCollection:
    """Tests for the SFDR Data Collection wrapper class."""

    @pytest.fixture
    def mock_sfdr_data(self) -> Mock:
        """Creates a mock SfdrData object with nested structure."""
        data = Mock()

        env = Mock()
        ghg = Mock()
        scope1 = Mock()
        scope1.value = 100.0
        scope1.data_source.page = 5
        scope1.data_source.file_reference = "file_123"

        ghg.scope1_ghg_emissions_in_tonnes = scope1
        env.greenhouse_gas_emissions = ghg

        env.water = None

        data.environmental = env
        return data

    def test_get_value_generic_success(self, mock_sfdr_data: Mock) -> None:
        """Test successful retrieval of a nested value."""
        collection = SFDRDataCollection(mock_sfdr_data)

        val = collection.get_value_generic(
            "environmental", "greenhouse_gas_emissions", "scope1_ghg_emissions_in_tonnes"
        )
        assert val == 100.0

    def test_get_value_generic_missing_category(self, mock_sfdr_data: Mock) -> None:
        """Test retrieval when a whole category is missing."""
        collection = SFDRDataCollection(mock_sfdr_data)
        collection.data.social = None

        val = collection.get_value_generic("social", "any_sub", "any_field")
        assert val is None

    def test_get_value_generic_missing_field(self, mock_sfdr_data: Mock) -> None:
        """Test retrieval when the final field is missing."""
        mock_sfdr_data.environmental.greenhouse_gas_emissions.non_existent_field = None
        collection = SFDRDataCollection(mock_sfdr_data)

        val = collection.get_value_generic("environmental", "greenhouse_gas_emissions", "non_existent_field")
        assert val is None

    def test_get_scope1_ghg_emissions(self, mock_sfdr_data: Mock) -> None:
        """Test the specific helper method for Scope 1."""
        collection = SFDRDataCollection(mock_sfdr_data)
        assert collection.get_scope1_ghg_emissions() == 100.0

    def test_get_scope1_page_number(self, mock_sfdr_data: Mock) -> None:
        """Test page number retrieval."""
        collection = SFDRDataCollection(mock_sfdr_data)
        assert collection.get_scope1_page_number() == 5

    def test_get_scope1_file_reference(self, mock_sfdr_data: Mock) -> None:
        """Test file reference retrieval."""
        collection = SFDRDataCollection(mock_sfdr_data)
        assert collection.get_scope1_file_reference() == "file_123"
