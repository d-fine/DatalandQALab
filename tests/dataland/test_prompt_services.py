from unittest.mock import Mock, patch

import pytest
from dataland_backend.models.yes_no import YesNo

from dataland_qa_lab.prompting_services import prompting_service
from dataland_qa_lab.review import generate_gpt_request, numeric_value_generator, yes_no_value_generator


@pytest.fixture
def mock_pdf() -> Mock:
    pdf = Mock()
    pdf.content = "This is a test PDF content."
    return pdf


def test_template_1(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(1, mock_pdf, "Revenue")
    assert "provide the answers of all 6 questions in template 1" in result


def test_template_2(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(2, mock_pdf, "Revenue")
    assert "Taxonomy-aligned economic activities (denominator)" in result


def test_template_3(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(3, mock_pdf, "Revenue")
    assert "Taxonomy-aligned economic activities (numerator)" in result


def test_template_4(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(4, mock_pdf, "Revenue")
    assert "Taxonomy-eligible but not taxonomy-aligned economic activities" in result


def test_template_5(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(5, mock_pdf, "Revenue")
    assert "Taxonomy non-eligible economic activities" in result


def test_invalid_template(mock_pdf: Mock) -> None:
    result = prompting_service.PromptingService.create_main_prompt(99, mock_pdf, "Revenue")
    assert result == "Invalid template"


def test_create_sub_prompt_template1() -> None:
    expected = {
        "type": "object",
        "properties": {
            "1": {
                "type": "string",
                "description": """The precise answer to the first question
                        of Nuclear energy related activities. "The undertaking carries out,
                        funds or has exposures to research, development, demonstration and
                        deployment of innovative electricity generation facilities that
                        produce energy from nuclear processes with minimal waste from
                        the fuel cycle." Write only Yes or No.
                        You need to answer this question.""",
            },
            "2": {
                "type": "string",
                "description": """The precise answer to the second question
                        of Nuclear energy related activities. "The undertaking carries out,
                        funds or has exposures to construction and safe operation of new
                        nuclear installations to produce electricity or process heat,
                        including for the purposes of district heating or industrial
                        processes such as hydrogen production, as well as their safety
                        upgrades, using best available technologies." Write only Yes or No
                        You need to answer this question.""",
            },
            "3": {
                "type": "string",
                "description": """The precise answer to the third question
                        of Nuclear energy related activities. "The undertaking carries out,
                        funds or has exposures to safe operation of existing nuclear
                        installations that produce electricity or process heat, including
                        for the purposes of district heating or industrial processes such
                        as hydrogen production from nuclear energy, as well as their safety
                        upgrades." Write only Yes or No
                        You need to answer this question.""",
            },
            "4": {
                "type": "string",
                "description": """The precise answer to question
                        of Fossil gas related activities. "The undertaking carries out,
                        funds or has exposures to construction or operation of
                        electricity generation facilities that produce electricity
                        using fossil gaseous fuels." Write only Yes or No
                        You need to answer this question.""",
            },
            "5": {
                "type": "string",
                "description": """The precise answer to the second or fifth question
                        of Fossil gas related activities. "The undertaking carries out,
                        funds or has exposures to construction, refurbishment, and
                        operation of combined heat/cool and power generation facilities
                        using fossil gaseous fuels." Write only Yes or No
                        You need to answer this question.""",
            },
            "6": {
                "type": "string",
                "description": """The precise answer to the third or sixth question
                        of Fossil gas related activities. "The undertaking carries out,
                        funds or has exposures to construction, refurbishment and
                        operation of heat generation facilities that produce heat/cool
                        using fossil gaseous fuels." Write only Yes or No
                        You need to answer this question.""",
            },
        },
        "required": [
            "answer_value_1",
            "answer_value_2",
            "answer_value_3",
            "answer_value_4",
            "answer_value_5",
            "answer_value_6",
        ],
    }
    result = prompting_service.PromptingService.create_sub_prompt_template1()
    assert expected == result


def test_create_sub_prompt_template2to4() -> None:
    rows = [1, 2, 3, 4, 5, 6, 7, 8]
    categories = ["CCM+CCA", "CCM", "CCA"]

    result = prompting_service.PromptingService.create_sub_prompt_template2to4("Revenue")
    properties = result["properties"]

    assert len(properties) == len(rows) * len(categories)
    for row in rows:
        for category in categories:
            key = f"answer_value_{category}%_row{row}"
            assert key in properties
            assert properties[key]["type"] == "string"
            assert f"percentage of {category} of row {row}" in properties[key]["description"]


def test_create_sub_prompt_template5() -> None:
    rows = [1, 2, 3, 4, 5, 6, 7, 8]

    result = prompting_service.PromptingService.create_sub_prompt_template5("Revenue")
    properties = result["properties"]

    assert len(properties) == len(rows), "The number of properties should match the number of rows."

    for row in rows:
        key = f"answer_value_%_row{row}"
        assert key in properties, f"The key '{key}' is missing."
        assert properties[key]["type"] == "string", f"The type of '{key}' should be of type string."
        assert "description" in properties[key], f"'{key}' should have a description."
        assert f"percentage of row {row}" in properties[key]["description"], f"The discription '{key}' is not correct."


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_yes_no_values_from_report(mock_generate_gpt_request: Mock, mock_pdf: Mock) -> None:
    mock_generate_gpt_request.return_value = ["Yes", "No", "Yes", "No", "Yes", "No"]

    result = yes_no_value_generator.get_yes_no_values_from_report(mock_pdf)

    mock_generate_gpt_request.assert_called_once_with(
        prompting_service.PromptingService.create_main_prompt(1, mock_pdf, "Revenue"),
        prompting_service.PromptingService.create_sub_prompt_template1(),
    )
    expected_result = {
        "nuclear_energy_related_activities_section426": YesNo("Yes"),
        "nuclear_energy_related_activities_section427": YesNo("No"),
        "nuclear_energy_related_activities_section428": YesNo("Yes"),
        "fossil_gas_related_activities_section429": YesNo("No"),
        "fossil_gas_related_activities_section430": YesNo("Yes"),
        "fossil_gas_related_activities_section431": YesNo("No"),
    }
    assert result == expected_result, "The return values do not match."


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_generate_gpt_request(mock_generate_gpt_request: Mock, mock_pdf: Mock) -> None:
    mock_generate_gpt_request.return_value = ["Yes", "No", "Yes", "No", "Yes", "No"]

    result = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
        prompting_service.PromptingService.create_main_prompt(1, mock_pdf, "Revenue"),
        prompting_service.PromptingService.create_sub_prompt_template1(),
    )

    mock_generate_gpt_request.assert_called_once_with(
        prompting_service.PromptingService.create_main_prompt(1, mock_pdf, "Revenue"),
        prompting_service.PromptingService.create_sub_prompt_template1(),
    )
    assert result == ["Yes", "No", "Yes", "No", "Yes", "No"], "The return values do not match."


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_alligned_denominator(mock_generate_gpt_request: Mock, mock_pdf: Mock) -> None:
    mock_generate_gpt_request.return_value = [0.1, 0, 0, 3.2, 0, 100]

    result = numeric_value_generator.NumericValueGenerator.get_taxonomy_alligned_denominator(mock_pdf, "Revenue")

    mock_generate_gpt_request.assert_called_once_with(
        prompting_service.PromptingService.create_main_prompt(2, mock_pdf, "Revenue"),
        prompting_service.PromptingService.create_sub_prompt_template2to4("Revenue"),
    )
    assert result == [0.1, 0, 0, 3.2, 0, 100], "The return values do not match."


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_alligned_numerator(mock_generate_gpt_request: Mock, mock_pdf: Mock) -> None:
    mock_generate_gpt_request.return_value = [0.1, 0, 0, 3.2, 0, 100]

    result = numeric_value_generator.NumericValueGenerator.get_taxonomy_alligned_numerator(mock_pdf, "Revenue")

    mock_generate_gpt_request.assert_called_once_with(
        prompting_service.PromptingService.create_main_prompt(3, mock_pdf, "Revenue"),
        prompting_service.PromptingService.create_sub_prompt_template2to4("Revenue"),
    )
    assert result == [0.1, 0, 0, 3.2, 0, 100], "The return values do not match."


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_eligible_not_alligned(mock_generate_gpt_request: Mock, mock_pdf: Mock) -> None:
    mock_generate_gpt_request.return_value = [0.1, 0, 0, 3.2, 0, 100]

    result = numeric_value_generator.NumericValueGenerator.get_taxonomy_eligible_not_alligned(mock_pdf, "Revenue")

    mock_generate_gpt_request.assert_called_once_with(
        prompting_service.PromptingService.create_main_prompt(4, mock_pdf, "Revenue"),
        prompting_service.PromptingService.create_sub_prompt_template2to4("Revenue"),
    )
    assert result == [0.1, 0, 0, 3.2, 0, 100], "The return values do not match."


@patch("dataland_qa_lab.review.generate_gpt_request.GenerateGptRequest.generate_gpt_request")
def test_get_taxonomy_non_eligible(mock_generate_gpt_request: Mock, mock_pdf: Mock) -> None:
    mock_generate_gpt_request.return_value = [0.1, 0, 0, 3.2, 0, 100]

    result = numeric_value_generator.NumericValueGenerator.get_taxonomy_non_eligible(mock_pdf, "Revenue")

    mock_generate_gpt_request.assert_called_once_with(
        prompting_service.PromptingService.create_main_prompt(5, mock_pdf, "Revenue"),
        prompting_service.PromptingService.create_sub_prompt_template5("Revenue"),
    )
    assert result == [0.1, 0, 0, 3.2, 0, 100], "The return values do not match."
