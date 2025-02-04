from unittest.mock import Mock, patch

import pytest

from dataland_qa_lab.prompting_services import prompting_service
from dataland_qa_lab.review.generate_gpt_request import GenerateGptRequest  # noqa: F401
from dataland_qa_lab.review.numeric_value_generator import NumericValueGenerator


# Mock AnalyzeResult
@pytest.fixture
def mock_analyze_result() -> Mock:
    mock_result = Mock()
    mock_result.content = "Test readable text content."
    return mock_result


# Mock Config and Logger
@pytest.fixture
def mock_logger() -> Mock:
    logger = Mock()
    return logger


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_aligned_denominator_success(mock_generate_gpt_request: Mock, mock_analyze_result: Mock) -> None:
    """Test successful extraction of taxonomy aligned denominator values."""
    mock_generate_gpt_request.return_value = ["0.1", "2.5", "3.0"]

    result = NumericValueGenerator.get_taxonomy_aligned_denominator(mock_analyze_result, "Revenue")

    mock_generate_gpt_request.assert_called_once_with(
        prompting_service.PromptingService.create_main_prompt(2, mock_analyze_result, "Revenue"),
        prompting_service.PromptingService.create_sub_prompt_template2to4("Revenue"),
    )

    assert result == [0.1, 2.5, 3.0]


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_aligned_denominator_empty_response(mock_generate_gpt_request: Mock) -> None:
    """Test empty GPT response for taxonomy aligned denominator values."""
    mock_generate_gpt_request.return_value = []

    with pytest.raises(ValueError, match=r"No results returned from GPT for template 2 values.") as exc:
        NumericValueGenerator.get_taxonomy_aligned_denominator("Some readable text", "Revenue")

    assert "No results returned from GPT for template 2 values." in str(exc.value)


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_aligned_denominator_conversion_error(
    mock_generate_gpt_request: Mock, mock_analyze_result: Mock
) -> None:
    """Test float conversion error in taxonomy aligned denominator values."""
    mock_generate_gpt_request.return_value = ["0.1", "invalid", "3.0"]

    with pytest.raises(ValueError) as exc:  # noqa: PT011
        NumericValueGenerator.get_taxonomy_aligned_denominator(mock_analyze_result, "Revenue")

    assert "Unexpected error during float conversion" in str(exc.value)


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_aligned_numerator_success(mock_generate_gpt_request: Mock, mock_analyze_result: Mock) -> None:
    """Test successful extraction of taxonomy aligned numerator values."""
    mock_generate_gpt_request.return_value = ["1.0", "2.0", "3.0"]

    result = NumericValueGenerator.get_taxonomy_aligned_numerator(mock_analyze_result, "Revenue")

    mock_generate_gpt_request.assert_called_once_with(
        prompting_service.PromptingService.create_main_prompt(3, mock_analyze_result, "Revenue"),
        prompting_service.PromptingService.create_sub_prompt_template2to4("Revenue"),
    )

    assert result == [1.0, 2.0, 3.0]


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_eligible_not_alligned_success(mock_generate_gpt_request: Mock, mock_analyze_result: Mock) -> None:
    """Test successful extraction of taxonomy eligible not aligned values."""
    mock_generate_gpt_request.return_value = ["4.0", "5.0", "6.0"]

    result = NumericValueGenerator.get_taxonomy_eligible_not_alligned(mock_analyze_result, "Revenue")

    mock_generate_gpt_request.assert_called_once_with(
        prompting_service.PromptingService.create_main_prompt(4, mock_analyze_result, "Revenue"),
        prompting_service.PromptingService.create_sub_prompt_template2to4("Revenue"),
    )

    assert result == [4.0, 5.0, 6.0]


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_non_eligible_success(mock_generate_gpt_request: Mock, mock_analyze_result: Mock) -> None:
    """Test successful extraction of taxonomy non-eligible values."""
    mock_generate_gpt_request.return_value = ["7.0", "8.0", "9.0"]

    result = NumericValueGenerator.get_taxonomy_non_eligible(mock_analyze_result, "Revenue")

    mock_generate_gpt_request.assert_called_once_with(
        prompting_service.PromptingService.create_main_prompt(5, mock_analyze_result, "Revenue"),
        prompting_service.PromptingService.create_sub_prompt_template5("Revenue"),
    )

    assert result == [7.0, 8.0, 9.0]


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_non_eligible_empty_response(mock_generate_gpt_request: Mock, mock_analyze_result: Mock) -> None:
    """Test empty GPT response for taxonomy non-eligible values."""
    mock_generate_gpt_request.return_value = []

    with pytest.raises(ValueError) as exc:  # noqa: PT011
        NumericValueGenerator.get_taxonomy_non_eligible(mock_analyze_result, "Revenue")

    assert "No results returned from GPT for template 5 values." in str(exc.value)


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_non_eligible_conversion_error(mock_generate_gpt_request: Mock, mock_analyze_result: Mock) -> None:
    """Test float conversion error in taxonomy non-eligible values."""
    mock_generate_gpt_request.return_value = ["7.0", "invalid", "9.0"]

    with pytest.raises(ValueError) as exc:  # noqa: PT011
        NumericValueGenerator.get_taxonomy_non_eligible(mock_analyze_result, "Revenue")

    assert "Unexpected error during float conversion" in str(exc.value)
