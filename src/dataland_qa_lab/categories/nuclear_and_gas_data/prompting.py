import json


class NuclearAndGasPrompting:
    prompt_xyz = ""

    def __init__(self) -> None:
        pass

    def run_prompt(self, field_name: str, pdf: str):
        print(field_name)
        match field_name:
            case "case_1":
                return ""

    def generate_prompt_case_1(pdf: str) -> str:
        json_subprompt = {
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

        return f"""Given the information from the [relevant documents],
        provide the answers of all 6 questions in template 1.
        Only answer with 'Yes' or 'No'. You need to provide 6 answers.
        # Relevant Documents
        {pdf}

        {json.dumps(json_subprompt, indent=4)}
        """

    @staticmethod
    def generate_prompt_case_2(pdf: str, kpi: str) -> str:
        """Prompt for template 2."""
        schema = NuclearAndGasPrompting._get_schema_template_2to4(kpi)

        return f"""
    For each row 1-8 of template 2 ({kpi}) it's called
                "Taxonomy-aligned economic activities (denominator)",
                give me the percentage of "CCM+CCA", "CCM" and "CCA" for all rows.
                Focus on the row numbers on the left side of the table.
                If you can't find the percentage value, write "-1".
                Consider translating for this given task like Meldebogen instead of template.
                # Relevant Documents
                {pdf}
                
                {json.dumps(schema, indent=4)}"""

    @staticmethod
    def generate_prompt_case_3(pdf: str, kpi: str) -> str:
        """Prompt for template 3."""
        schema = NuclearAndGasPrompting._get_schema_template_2to4(kpi)

        return f"""For each row 1-8 of template 3 ({kpi}) it's called
                "Taxonomy-aligned economic activities (numerator)",
                give me the percentage of "CCM+CCA", "CCM" and "CCA" for all rows.
                Focus on the row numbers on the left side of the table.
                If you can't find the percentage value, write "-1".
                Consider translating for this given task like Meldebogen instead of template.
                # Relevant Documents
                {pdf}
                
                {json.dumps(schema, indent=4)}
                """

    @staticmethod
    def generate_prompt_case_4(pdf: str, kpi: str) -> str:
        """Prompt for template 4."""
        schema = NuclearAndGasPrompting._get_schema_template_2to4(kpi)

        return f"""For each row 1-8 of template 4 ({kpi}) it's called
                "Taxonomy-eligible but not taxonomy-aligned economic activities",
                give me the percentage of "CCM+CCA", "CCM" and "CCA" for all rows.
                Focus on the row numbers on the left side of the table.
                If you can't find the percentage value, write "-1".
                Consider translating for this given task like Meldebogen instead of template.
                # Relevant Documents
                {pdf}
                
                {json.dumps(schema, indent=4)}
                """

    @staticmethod
    def generate_prompt_case_5(pdf: str, kpi: str) -> str:
        """Prompt for template 5."""
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

        return f"""For each row 1-8 of template 5 ({kpi}) it's called
                "Taxonomy non-eligible economic activities",
                give me the percentage for all rows.
                Focus on the row numbers on the left side of the table.
                If you can't find the percentage value, write "-1".
                Consider translating for this given task like Meldebogen instead of template.
                # Relevant Documents
                {pdf}
                
                {json.dumps(schema, indent=4)}
                """

    @staticmethod
    def _get_schema_template_2to4(kpi: str) -> dict:
        """Helper to generate the schema for templates 2, 3, and 4."""
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
                schema["required"].append(value_key)
        return schema
