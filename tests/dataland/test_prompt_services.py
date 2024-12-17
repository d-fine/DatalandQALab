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

    result = prompting_service.PromptingService.create_sub_prompt_template2to4()
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

    result = prompting_service.PromptingService.create_sub_prompt_template5()
    properties = result["properties"]

    assert len(properties) == len(rows), "Die Anzahl der 'properties' sollte der Anzahl der Reihen entsprechen."

    for row in rows:
        key = f"answer_value_%_row{row}"
        assert key in properties, f"Der Schlüssel '{key}' fehlt in den Properties."
        assert properties[key]["type"] == "string", f"Der Typ von '{key}' sollte 'string' sein."
        assert "description" in properties[key], f"'{key}' sollte eine Beschreibung haben."
        assert f"percentage of row {row}" in properties[key]["description"], \
            f"Die Beschreibung von '{key}' ist nicht korrekt."
