class PromptingService:
    """Service for handling prompt requests."""

    @staticmethod
    def create_main_prompt(template: int, pdf: str, kpi: str) -> str:
        """Creates the main prompt for each template.

        Returns:
            str: The string of the main prompt.
        """
        match template:
            case 1:
                return f"""Given the information from the [relevant documents],
                provide the answers of all 6 questions in template 1.
                Only answer with 'Yes' or 'No'. You need to provide 6 answers.
                # Relevant Documents
                {pdf}
                """
            case 2:
                return f"""For each row 1-8 of template 2 ({kpi}) it's called
                "Taxonomy-aligned economic activities (denominator)",
                give me the percentage of "CCM+CCA", "CCM" and "CCA" for all rows.
                Focus on the row numbers on the left side of the table.
                If you can't find the percentage value, write "-1".
                Consider translating for this given task like Meldebogen instead of template.
                # Relevant Documents
                {pdf}
                """
            case 3:
                return f"""For each row 1-8 of template 3 ({kpi}) it's called
                "Taxonomy-aligned economic activities (numerator)",
                give me the percentage of "CCM+CCA", "CCM" and "CCA" for all rows.
                Focus on the row numbers on the left side of the table.
                If you can't find the percentage value, write "-1".
                Consider translating for this given task like Meldebogen instead of template.
                # Relevant Documents
                {pdf}
                """
            case 4:
                return f"""For each row 1-8 of template 4 ({kpi}) it's called
                "Taxonomy-eligible but not taxonomy-aligned economic activities",
                give me the percentage of "CCM+CCA", "CCM" and "CCA" for all rows.
                Focus on the row numbers on the left side of the table.
                If you can't find the percentage value, write "-1".
                Consider translating for this given task like Meldebogen instead of template.
                # Relevant Documents
                {pdf}
                """
            case 5:
                return f"""For each row 1-8 of template 5 ({kpi}) it's called
                "Taxonomy non-eligible economic activities",
                give me the percentage for all rows.
                Focus on the row numbers on the left side of the table.
                If you can't find the percentage value, write "-1".
                Consider translating for this given task like Meldebogen instead of template.
                # Relevant Documents
                {pdf}
                """
            case _:
                return "Invalid template"

    @staticmethod
    def create_sub_prompt_template1() -> dict:
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
    def create_sub_prompt_template2to4(kpi: str) -> dict:
        """Generates a schema for template 2 to 4.

        Returns:
            dict: A dictionary representing the schema.
        """
        rows = [1, 2, 3, 4, 5, 6, 7, 8]
        schema = {"type": "object", "properties": {}, "required": []}

        for row in rows:
            for category in ["CCM+CCA", "CCM", "CCA"]:
                value_key = f"answer_value_{category}%_row{row}"

                schema["properties"][value_key] = {
                    "type": "string",
                    "description": f"""The precise answer to the percentage of {category} of row {row}.
                    Write the number without the % symbol. If the value is not available, write '-1'.
                    Make sure to use the {kpi} value""",
                }

                schema["required"].extend([value_key])

        return schema

    @staticmethod
    def create_sub_prompt_template5(kpi: str) -> dict:
        """Generates a schema for template 5.

        Returns:
            dict: A dictionary representing the schema.
        """
        rows = [1, 2, 3, 4, 5, 6, 7, 8]
        schema = {"type": "object", "properties": {}, "required": []}

        for row in rows:
            value_key = f"answer_value_%_row{row}"

            schema["properties"][value_key] = {
                "type": "string",
                "description": f"""The precise answer to the percentage of row {row}.
                Write the number without the % symbol. If the value is not available, write '-1'.
                Make sure to use the {kpi} value""",
            }

            schema["required"].extend([value_key])

        return schema
