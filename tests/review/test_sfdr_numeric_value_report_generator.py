from unittest.mock import Mock, patch

import pytest

from dataland_qa_lab.review.report_generator.sfdr_numeric_value_generator import SFDRNumericValueGenerator


class TestSFDRNumericValueGenerator:
    """Tests for the SFDR Numeric Value Generator class."""

    @patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
    def test_get_scope1_emissions_success(self, mock_gpt_request: Mock) -> None:
        """Test successful extraction of Scope 1 emissions."""

        mock_gpt_request.return_value = ["12345.67"]

        result = SFDRNumericValueGenerator.get_scope1_emissions("markdown text")

        assert result == 12345.67
        mock_gpt_request.assert_called_once()

    @patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
    def test_get_generic_numeric_value_success(self, mock_gpt_request: Mock) -> None:
        """Test successful generic extraction."""
        mock_gpt_request.return_value = ["50.5"]

        result = SFDRNumericValueGenerator.get_generic_numeric_value("text", "Water", "tonnes")

        assert result == 50.5

    @patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
    def test_get_generic_numeric_value_not_found(self, mock_gpt_request: Mock) -> None:
        """Test that -1 from GPT is converted to None."""
        mock_gpt_request.return_value = ["-1"]

        result = SFDRNumericValueGenerator.get_generic_numeric_value("text", "Water", "tonnes")

        assert result is None

    @patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
    def test_get_generic_numeric_value_empty_response(self, mock_gpt_request: Mock) -> None:
        """Test handling of empty GPT response."""
        mock_gpt_request.return_value = []

        result = SFDRNumericValueGenerator.get_generic_numeric_value("text", "Water", "tonnes")

        assert result is None

    @patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
    def test_get_generic_numeric_value_exception(self, mock_gpt_request: Mock) -> None:
        """Test exception handling during request."""
        mock_gpt_request.side_effect = Exception("API Error")

        result = SFDRNumericValueGenerator.get_generic_numeric_value("text", "Water", "tonnes")

        assert result is None

    def test_extract_number_integers(self) -> None:
        assert SFDRNumericValueGenerator.extract_number(100) == 100.0

    def test_extract_number_floats(self) -> None:
        assert SFDRNumericValueGenerator.extract_number(50.5) == 50.5

    def test_extract_number_string_simple(self) -> None:
        assert SFDRNumericValueGenerator.extract_number("123.45") == 123.45

    def test_extract_number_string_with_comma(self) -> None:
        """Test removal of thousands separator."""
        assert SFDRNumericValueGenerator.extract_number("1,234.56") == 1234.56

    def test_extract_number_string_with_text(self) -> None:
        """Test regex extraction from mixed text."""
        assert SFDRNumericValueGenerator.extract_number("Value is 500 tonnes") == 500.0

    def test_extract_number_invalid(self) -> None:
        """Test that invalid strings raise ValueError."""
        with pytest.raises(ValueError):
            SFDRNumericValueGenerator.extract_number("No number here")

