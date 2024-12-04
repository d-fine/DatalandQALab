import json

from openai import AzureOpenAI

from dataland_qa_lab.utils import config


class TemplateExtractor:
    """A class to handle the extraction of templates using Azure OpenAI."""

    def __init__(self) -> None:
        """Initializes the class."""

    @staticmethod
    def extract_template(prompt: str, schema: dict) -> list:
        """Extracts information from any template using Azure OpenAI and returns a list of results.

        Args:
            prompt (str): The prompt to be processed
            schema (dict): The schema to be used for the extraction.
            rows (list): A list of row numbers.

        Returns:
            list: A list of extracted information.
        """
        conf = config.get_config()

        client = AzureOpenAI(
            api_key=conf.azure_openai_api_key,
            api_version="2024-07-01-preview",
            azure_endpoint=conf.azure_openai_endpoint,
        )

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
                        "parameters": schema,
                    },
                }
            ],
        )
        tool_call = updated_openai_response.choices[0].message.tool_calls[0].function
        return TemplateExtractor.format_json(tool_call.arguments)

    @staticmethod
    def format_json(arguments: str) -> list:
        """Format the JSON arguments.

        Args:
            arguments (dict): The arguments to be formatted.

        Returns:
            str: The formatted JSON arguments.
        """
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
