from pathlib import Path
from typing import Any
from unittest import mock

from azure.ai.documentintelligence.models import AnalyzeResult
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice

from dataland_qa_lab.dataland import company_data, data_extraction, prompt_schema, template_extractor


def test_generate_schema_for_rows() -> None:
    # Test Input
    rows = [1, 2]
    ps = prompt_schema.PromptSchema()
    # Erwartetes Ergebnis (auszugsweise)
    expected_properties = {
        "answer_value_CCM+CCA€_row1": {
            "type": "number",
            "description": """The precise answer to the € of CCM+CCA of row 1
                        without any thousand separators.""",
        },
        "answer_currency_CCM+CCA€_row1": {
            "type": "string",
            "description": """The currency of the answer to the € of CCM+CCA of row 1
                        (e.g. €, $, Mio.€, Mio.$, M$, € in thousends)""",
        },
    }

    # Aufruf der Methode
    actual_schema = ps.generate_schema_for_rows(rows)

    # Test: Typ und Struktur überprüfen
    assert actual_schema["type"] == "object"
    assert "properties" in actual_schema
    assert "required" in actual_schema

    # Test: Inhalte stichprobenartig überprüfen
    assert (
        actual_schema["properties"]["answer_value_CCM+CCA€_row1"] == expected_properties["answer_value_CCM+CCA€_row1"]
    )
    assert "answer_value_CCM+CCA€_row1" in actual_schema["required"]

    # Test für eine andere Zeile (z. B. Row 2)
    assert "answer_value_CCM+CCA%_row2" in actual_schema["properties"]
    assert "answer_currency_CCM+CCA%_row2" in actual_schema["required"]

    # Anzahl der Properties und Required Keys überprüfen
    total_properties = len(rows) * 6 * 2  # 6 Kategorien, 2 Werte pro Kategorie
    assert len(actual_schema["properties"]) == total_properties
    assert len(actual_schema["required"]) == total_properties


def test_generate_schema_for_template1() -> None:
    # Erwartetes Ergebnis
    ps = prompt_schema.PromptSchema()
    expected_schema = {
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

    # Aufruf der Methode
    actual_schema = ps.generate_schema_for_template1()

    # Prüfen, ob die Struktur korrekt ist
    assert actual_schema["type"] == "object"
    assert "properties" in actual_schema
    assert "required" in actual_schema

    # Stichprobenhafte Überprüfung von Properties
    for key in ["1", "2", "3", "4", "5", "6"]:
        assert key in actual_schema["properties"]
        assert actual_schema["properties"][key]["type"] == "string"
        assert "description" in actual_schema["properties"][key]

    # Überprüfen, dass alle erforderlichen Felder enthalten sind
    assert len(actual_schema["required"]) == len(expected_schema["required"])
    for required_key in expected_schema["required"]:
        assert required_key in actual_schema["required"]

    # Überprüfen, dass das Schema korrekt mit dem Erwarteten übereinstimmt
    assert actual_schema == expected_schema


def test_generate_schema_template5() -> None:
    # Testdaten: Beispielhafte Reihen
    rows = [1]
    ps = prompt_schema.PromptSchema()
    # Erwartetes Ergebnis
    expected_schema = {
        "type": "object",
        "properties": {
            "answer_value_€_row1": {
                "type": "number",
                "description": """The precise answer to the € of row 1
                    without any thousand separators.""",
            },
            "answer_currency_€_row1": {
                "type": "string",
                "description": """The currency of the answer to the € of row 1
                    (e.g. €, $, Mio.€, Mio.$, M$, € in thousends)""",
            },
            "answer_value_%_row1": {
                "type": "number",
                "description": "The precise answer to the percentage of row 1.",
            },
            "answer_currency_%_row1": {
                "type": "string",
                "description": "%",
            },
        },
        "required": [
            "answer_value_€_row1",
            "answer_currency_€_row1",
            "answer_value_%_row1",
            "answer_currency_%_row1",
        ],
    }

    # Aufruf der Methode
    actual_schema = ps.generate_schema_tmeplate5(rows)

    # Überprüfen der Schema-Struktur
    assert actual_schema["type"] == "object"
    assert "properties" in actual_schema
    assert "required" in actual_schema

    # Überprüfen der Keys in den Properties
    for row in rows:
        for metric in ["€", "%"]:
            value_key = f"answer_value_{metric}_row{row}"
            currency_key = f"answer_currency_{metric}_row{row}"

            assert value_key in actual_schema["properties"]
            assert currency_key in actual_schema["properties"]

            # Validierung der Feldinhalte
            if metric == "€":
                assert actual_schema["properties"][value_key]["type"] == "number"
                assert "without any thousand separators" in actual_schema["properties"][value_key]["description"]

                assert actual_schema["properties"][currency_key]["type"] == "string"
                assert (
                    "(e.g. €, $, Mio.€, Mio.$, M$, € in thousends)"
                    in actual_schema["properties"][currency_key]["description"]
                )
            else:
                assert actual_schema["properties"][value_key]["type"] == "number"
                assert "percentage" in actual_schema["properties"][value_key]["description"]

                assert actual_schema["properties"][currency_key]["type"] == "string"
                assert actual_schema["properties"][currency_key]["description"] == "%"

    # Validieren der Required-Felder
    assert sorted(actual_schema["required"]) == sorted(expected_schema["required"])

    # Vergleich mit dem gesamten erwarteten Schema
    assert actual_schema == expected_schema


def create_document_intelligence_mock() -> AnalyzeResult:
    return AnalyzeResult(content="")


def build_simple_openai_chat_completion(message: str) -> ChatCompletion:
    return ChatCompletion(
        id="test",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content=message,
                    role="assistant",
                ),
            )
        ],
        created=0,
        model="test",
        object="chat.completion",
    )


@mock.patch("openai.resources.chat.Completions.create", return_value=build_simple_openai_chat_completion("No"))
@mock.patch(
    "dataland_qa_lab.dataland.data_extraction.extract_text_of_pdf", return_value=create_document_intelligence_mock()
)
def test_extract_page(mock_create: Any, mock_extract_text_of_pdf: Any) -> None:  # noqa: ANN401, ARG001
    project_root = Path(__file__).resolve().parent.parent.parent
    path = project_root / "data" / "pdfs" / "covestro.pdf"
    page_tmp = company_data.CompanyData.get_company_pages()
    page = page_tmp[1]

    actual_result = data_extraction.ectract_page(page[0], path)

    assert actual_result == AnalyzeResult(content="")


def test_extract_template() -> None:
    arguments = """{"1": "No", "2": "No", "3": "No", "4": "No", "5": "Yes", "6": "No"}"""
    te = template_extractor.TemplateExtractor()
    result = te.format_json(arguments)
    # Erwartetes Ergebnis
    expected_result = """row1: ['No']"""

    # Test
    assert result[0] == expected_result, f"Expected {expected_result}, but got {result}"
