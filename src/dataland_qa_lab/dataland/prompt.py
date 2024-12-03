import json

from openai import AzureOpenAI
from pypdf import PdfReader

import dataland_qa_lab.dataland.data_extraction as qa_lab
from dataland_qa_lab.dataland.data_extraction import AnalyzeResult
from dataland_qa_lab.utils import config


def extract_template1(prompt: str) -> list:
    """Extracts information from template 1 using Azure OpenAI and returns a list of results.

    Args:
        prompt (str): The prompt to be processed.

    Returns:
        list: A list of extracted information.
    """
    conf = config.get_config()

    client = AzureOpenAI(
        api_key=conf.azure_openai_api_key, api_version="2024-07-01-preview", azure_endpoint=conf.azure_openai_endpoint
    )

    row = [1, 2, 3, 4, 5, 6]

    updated_openai_response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": prompt},
        ],
        tool_choice="required",
        tools=[
        {
            "type": "function",
                "function": {
                    "name": "requested_information_precisely_found_in_relevant_documents",
                    "description": "Submit the requested information. "
                    "Use this function when the information is precisely stated in the relevant documents. ",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "1": {
                                "type": "string",
                                "description": """The precise answer to the first question 
                                of Nuclear energy related activities. Write only Yes or NO"""
                            },
                            "2": {
                                "type": "string",
                                "description": "The precise answer to the second question of Nuclear energy related activities. Write only Yes or NO"
                            },
                            "3": {
                                "type": "string",
                                "description": "The precise answer to the third question of Nuclear energy related activities. Write only Yes or NO"
                            },
                            "4": {
                                "type": "string",
                                "description": "The precise answer to the first question of Fossil gas related activities. Write only Yes or NO"
                            },
                            "5": {
                                "type": "string",
                                "description": "The precise answer tto the second question of Fossil gas related activities. Write only Yes or NO"
                            },
                            "6": {
                                "type": "string",
                                "description": "TThe precise answer to the third question of Fossil gas related activities. Write only Yes or NO"
                            },
                        },
                        "required": ["answer_value_1", "answer_value_2", "answer_value_3", "answer_value_4", "answer_value_5", "answer_value_6"],
                    }
                },
            }
        ],
    )
    tool_call = updated_openai_response.choices[0].message.tool_calls[0].function

    # Dein Argument-String (vollständig)
    arguments = tool_call.arguments

    # Konvertiere den String in ein Python-Dictionary
    data = json.loads(arguments)

    # Gruppiere nach Zeilen, aber nur mit Werten
    grouped_data = {}
    for key, value in data.items():
        row_key = key.split("_row")[-1]
        group_key = f"row{row_key}"
        grouped_data.setdefault(group_key, [])
        grouped_data[group_key].append(value)

    result = []
    # Jede Zeile in einer Zeile ausgeben
    for row, values in grouped_data.items():
        result.append(f"{row}: {values}")

    return result


def ectract_page(page_tmp: int, pdf_tmp: str) -> AnalyzeResult:
    """Extracts text from a specific page of a PDF and returns the analysis result.

    Args:
        page_tmp (int): The page number to extract.
        pdf_tmp (str): The path to the PDF file.

    Returns:
        AnalyzeResult: The result of the text extraction analysis.
    """
    path = pdf_tmp
    page = page_tmp

    reader = PdfReader(path)
    pdf_bytes = qa_lab.get_relevant_page_of_pdf(page=page, full_pdf=reader)
    analyze_result = qa_lab.extract_text_of_pdf(pdf_bytes)
    return analyze_result


def extract_template2(prompt: str) -> list:
    """Extracts information from template 2 using Azure OpenAI and returns a list of results.

    Args:
        prompt (str): The prompt to be processed.

    Returns:
        list: A list of extracted information.
    """
    conf = config.get_config()

    client = AzureOpenAI(
        api_key=conf.azure_openai_api_key, api_version="2024-07-01-preview", azure_endpoint=conf.azure_openai_endpoint
    )

    row = [1, 2, 3, 4, 5, 6, 7, 8]

    schema = generate_schema_for_rows(row)

    updated_openai_response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": prompt},
        ],
        tool_choice="required",
        tools=[
        {
            "type": "function",
                "function": {
                    "name": "requested_information_precisely_found_in_relevant_documents",
                    "description": "Submit the requested information. "
                    "Use this function when the information is precisely stated in the relevant documents. ",
                    "parameters": schema
                },
            }
        ],
    )
    tool_call = updated_openai_response.choices[0].message.tool_calls[0].function

    # Dein Argument-String (vollständig)
    arguments = tool_call.arguments

    # Konvertiere den String in ein Python-Dictionary
    data = json.loads(arguments)

    # Gruppiere nach Zeilen, aber nur mit Werten
    grouped_data = {}
    for key, value in data.items():
        row_key = key.split("_row")[-1]
        group_key = f"row{row_key}"
        grouped_data.setdefault(group_key, [])
        grouped_data[group_key].append(value)

    result = []
    # Jede Zeile in einer Zeile ausgeben
    for row, values in grouped_data.items():
        result.append(f"{row}: {values}")

    return result


def generate_schema_for_rows(rows: list) -> dict:
    """Generates a schema for the given rows.

    Args:
        rows (list): A list of row numbers.

    Returns:
        dict: A dictionary representing the schema.
    """
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    # Für jede Zeile Felder hinzufügen
    for row in rows:
        for category in ["CCM+CCA", "CCM", "CCA"]:
            for metric, value_type in [("€", "number"), ("%", "number")]:
                value_key = f"answer_value_{category}{metric}_row{row}"
                currency_key = f"answer_currency_{category}{metric}_row{row}"

                # Hinzufügen von Eigenschaften
                schema["properties"][value_key] = {
                    "type": value_type,
                    "description": f"""The precise answer to the {metric} of {category} of row {row}
                    without any thousand separators.""" 
                    if metric == "€" else f"The precise answer to the percentage of {category} of row {row}."
                }
                schema["properties"][currency_key] = {
                    "type": "string",
                    "description": f""""The currency of the answer to the {metric} of {category} of row {row}
                    (e.g. €, $, Mio.€, Mio.$, M$, € in thousends)" if metric == "€" else "Always use %."""
                }

                # Hinzufügen zu required
                schema["required"].extend([value_key, currency_key])

    return schema

def generate_schema_tmeplate5(rows):
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    # Für jede Zeile Felder hinzufügen
    for row in rows:
        for metric, value_type in [("€", "number"), ("%", "number")]:
            value_key = f"answer_value_{metric}_row{row}"
            currency_key = f"answer_currency_{metric}_row{row}"
            
            # Hinzufügen von Eigenschaften
            schema["properties"][value_key] = {
                "type": value_type,
                "description": f"The precise answer to the {metric} of row {row} without any thousand separators." if metric == "€" else f"The precise answer to the percentage of row {row}."
            }
            schema["properties"][currency_key] = {
                "type": "string",
                "description": f"The currency of the answer to the {metric} of row {row} (e.g. €, $, Mio.€, Mio.$, M$, € in thousends)" if metric == "€" else "Always use %."
            }

            # Hinzufügen zu required
            schema["required"].extend([value_key, currency_key])

    return schema


def extract_template5(prompt: str) -> list:
    """Extracts information from template 5 using Azure OpenAI and returns a list of results.

    Args:
        prompt (str): The prompt to be processed.

    Returns:
        list: A list of extracted information.
    """
    conf = config.get_config()

    client = AzureOpenAI(
        api_key=conf.azure_openai_api_key, api_version="2024-07-01-preview", azure_endpoint=conf.azure_openai_endpoint
    )

    row = [1, 2, 3, 4, 5, 6, 7, 8]

    schema = generate_schema_tmeplate5(row)

    updated_openai_response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": prompt},
        ],
        tool_choice="required",
        tools=[
        {
            "type": "function",
                "function": {
                    "name": "requested_information_precisely_found_in_relevant_documents",
                    "description": "Submit the requested information. "
                    "Use this function when the information is precisely stated in the relevant documents. ",
                    "parameters": schema
                },
            }
        ],
    )
    tool_call = updated_openai_response.choices[0].message.tool_calls[0].function

    # Dein Argument-String (vollständig)
    arguments = tool_call.arguments

    # Konvertiere den String in ein Python-Dictionary
    data = json.loads(arguments)

    # Gruppiere nach Zeilen, aber nur mit Werten
    grouped_data = {}
    for key, value in data.items():
        row_key = key.split("_row")[-1]
        group_key = f"row{row_key}"
        grouped_data.setdefault(group_key, [])
        grouped_data[group_key].append(value)

    result = []
    # Jede Zeile in einer Zeile ausgeben
    for row, values in grouped_data.items():
        result.append(f"{row}: {values}")

    return result
