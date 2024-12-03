class PromptSchema:
    """Generates a schema for a prompt."""

    def __init__(self) -> None:
        """Initializes the PromptSchema class."""

    @staticmethod
    def generate_schema_for_template1() -> dict:
        """Generates a schema for template 1.

        Returns:
            dict: A dictionary representing the schema for template 1.
        """
        return {
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

    @staticmethod
    def generate_schema_for_rows(rows: list) -> dict:
        """Generates a schema for the given rows.

        Args:
            rows (list): A list of row numbers.

        Returns:
            dict: A dictionary representing the schema.
        """
        schema = {"type": "object", "properties": {}, "required": []}

        for row in rows:
            for category in ["CCM+CCA", "CCM", "CCA"]:
                for metric, value_type in [("€", "number"), ("%", "number")]:
                    value_key = f"answer_value_{category}{metric}_row{row}"
                    currency_key = f"answer_currency_{category}{metric}_row{row}"

                    schema["properties"][value_key] = {
                        "type": value_type,
                        "description": f"""The precise answer to the {metric} of {category} of row {row}
                        without any thousand separators."""
                        if metric == "€"
                        else f"The precise answer to the percentage of {category} of row {row}.",
                    }
                    schema["properties"][currency_key] = {
                        "type": "string",
                        "description": f""""The currency of the answer to the {metric} of {category} of row {row}
                        (e.g. €, $, Mio.€, Mio.$, M$, € in thousends)"""
                        if metric == "€"
                        else "%",
                    }

                    # Hinzufügen zu required
                    schema["required"].extend([value_key, currency_key])

        return schema

    @staticmethod
    def generate_schema_tmeplate5(rows: list) -> dict:
        """Generates a schema for the given rows.

        Args:
            rows (list): A list of row numbers.

        Returns:
            dict: A dictionary representing the schema.
        """
        schema = {"type": "object", "properties": {}, "required": []}

        # Für jede Zeile Felder hinzufügen
        for row in rows:
            for metric, value_type in [("€", "number"), ("%", "number")]:
                value_key = f"answer_value_{metric}_row{row}"
                currency_key = f"answer_currency_{metric}_row{row}"

                schema["properties"][value_key] = {
                    "type": value_type,
                    "description": f"""The precise answer to the {metric} of row {row}
                    without any thousand separators."""
                    if metric == "€"
                    else f"The precise answer to the percentage of row {row}.",
                }
                schema["properties"][currency_key] = {
                    "type": "string",
                    "description": f"""The currency of the answer to the {metric} of row {row}
                    (e.g. €, $, Mio.€, Mio.$, M$, € in thousends)"""
                    if metric == "€"
                    else "%",
                }

                schema["required"].extend([value_key, currency_key])

        return schema
