from pathlib import Path

from dataland_qa_lab.dataland import company_data, data_extraction, prompt_schema, prompts, template_extractor


def test_prompt_engineering() -> None:
    ps = prompt_schema.PromptSchema()
    te = template_extractor.TemplateExtractor()
    prompt = prompts.Prompts()
    data = company_data.CompanyData()

    rows_6 = [1, 2, 3, 4, 5, 6]
    rows_8 = [1, 2, 3, 4, 5, 6, 7, 8]

    project_root = Path(__file__).resolve().parent.parent.parent

    data.get_company_pdf()
    page_tmp = data.get_company_pages()
    pdf = project_root / "data" / "pdfs" / "covestro.pdf"
    page = page_tmp[1]

    result = []

    if page[0] is not None:
        result.append(
            te.extract_template(
                prompt.generate_prompt_for_template1(data_extraction.ectract_page(page[0], pdf)),
                ps.generate_schema_for_template1(),
                rows_6,
            )
        )

    if page[1] is not None:
        result.append(
            te.extract_template(
                prompt.generate_prompt_for_template2(data_extraction.ectract_page(page[1], pdf)),
                ps.generate_schema_for_rows(rows_8),
                rows_8,
            )
        )

    if page[2] is not None:
        result.append(
            te.extract_template(
                prompt.generate_prompt_for_template3(data_extraction.ectract_page(page[2], pdf)),
                ps.generate_schema_for_rows(rows_8),
                rows_8,
            )
        )

    if page[3] is not None:
        result.append(
            te.extract_template(
                prompt.generate_prompt_for_template4(data_extraction.ectract_page(page[3], pdf)),
                ps.generate_schema_for_rows(rows_8),
                rows_8,
            )
        )

    if page[4] is not None:
        result.append(
            te.extract_template(
                prompt.generate_prompt_for_template5(data_extraction.ectract_page(page[4], pdf)),
                ps.generate_schema_tmeplate5(rows_8),
                rows_8,
            )
        )

    assert len(result) == 5


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
                        of Nuclear energy related activities. Write only Yes or No""",
            },
            "2": {
                "type": "string",
                "description": """The precise answer to the second question
                        of Nuclear energy related activities. Write only Yes or No""",
            },
            "3": {
                "type": "string",
                "description": """The precise answer to the third question
                        of Nuclear energy related activities. Write only Yes or No""",
            },
            "4": {
                "type": "string",
                "description": """The precise answer to the first question
                        of Fossil gas related activities. Write only Yes or No""",
            },
            "5": {
                "type": "string",
                "description": """The precise answer tto the second question
                        of Fossil gas related activities. Write only Yes or No""",
            },
            "6": {
                "type": "string",
                "description": """The precise answer to the third question
                        of Fossil gas related activities. Write only Yes or No""",
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
