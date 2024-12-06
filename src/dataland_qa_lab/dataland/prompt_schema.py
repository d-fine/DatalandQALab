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

    @staticmethod
    def generate_schema_for_rows() -> dict:
        """Generates a schema for the given rows.

        Args:
            rows (list): A list of row numbers.

        Returns:
            dict: A dictionary representing the schema.
        """
        rows = [1, 2, 3, 4, 5, 6, 7, 8]
        schema = {"type": "object", "properties": {}, "required": []}

        for row in rows:
            for category in ["CCM+CCA", "CCM", "CCA"]:
                for metric, value_type in [("%", "number")]:
                    value_key = f"answer_value_{category}{metric}_row{row}"
                    currency_key = f"answer_currency_{category}{metric}_row{row}"

                    schema["properties"][value_key] = {
                        "type": value_type,
                        "description": f"""The precise answer to the percentage of {category} of row {row}."""
                    }
                    schema["properties"][currency_key] = {
                        "type": "string",
                        "description": "%",
                    }

                    # Hinzufügen zu required
                    schema["required"].extend([value_key, currency_key])

        return schema

    @staticmethod
    def generate_schema_tmeplate5() -> dict:
        """Generates a schema for the given rows.

        Args:
            rows (list): A list of row numbers.

        Returns:
            dict: A dictionary representing the schema.
        """
        rows = [1, 2, 3, 4, 5, 6, 7, 8]
        schema = {"type": "object", "properties": {}, "required": []}

        # Für jede Zeile Felder hinzufügen
        for row in rows:
            for metric, value_type in [("%", "number")]:
                value_key = f"answer_value_{metric}_row{row}"
                currency_key = f"answer_currency_{metric}_row{row}"

                schema["properties"][value_key] = {
                    "type": value_type,
                    "description": f"The precise answer to the percentage of row {row}."
                }
                schema["properties"][currency_key] = {
                    "type": "string",
                    "description": "%",
                }

                schema["required"].extend([value_key, currency_key])

        return schema
