from unittest.mock import Mock

import pytest

from dataland_qa_lab.prompting_services import prompting_service


@pytest.fixture
def mock_pdf() -> Mock:
    pdf = Mock()
    pdf.content = "This is a test PDF content."
    return pdf


def test_template_1(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(1, mock_pdf)
    assert "provide the answers of all 6 questions in template 1" in result


def test_template_2(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(2, mock_pdf)
    assert "Taxonomy-aligned economic activities (denominator)" in result


def test_template_3(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(3, mock_pdf)
    assert "Taxonomy-aligned economic activities (numerator)" in result


def test_template_4(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(4, mock_pdf)
    assert "Taxonomy-eligible but not taxonomy-aligned economic activities" in result


def test_template_5(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(5, mock_pdf)
    assert "Taxonomy non-eligible economic activities" in result


def test_invalid_template(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(99, mock_pdf)
    assert result == "Invalid template"
