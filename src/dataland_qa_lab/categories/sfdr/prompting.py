class SFDRPrompting:
    prompt_xyz = ""

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def create_scope1_prompt(markdown_text: str) -> str:
        """Creates the prompt specifically for extracting Scope 1 GHG emissions."""
        return f"""
        You are an ESG analyst. From the given text, extract the numeric value of "Scope 1 GHG emissions".

        Rules:
        - Only use information explicitly stated in the text. Do not infer or assume any values.
        - Look strictly for direct (Scope 1) greenhouse gas emissions.
        - The unit must be tonnes of CO2e (for example tCO2, metric tons and so on).
        - Ignore Scope 2 or Scope 3 data completely.
        - If multiple years are reported, take the most recent one.
        - Return ONLY the number as a float (e.g., 12345.67). If not found, return null.

        Here is an Example:
        Text: "In 2023, total Scope 1 emissions amounted to 15,000 tCO2e."
        Output: 15000.0

        # Relevant Documents
        {markdown_text}
        """

    @staticmethod
    def create_scope1_schema() -> dict:
        """Generates the JSON schema for Scope 1 expected output."""
        return {
            "type": "object",
            "properties": {
                "scope1_value": {
                    "type": ["number", "null"],
                    "description": (
                        "Extracted numeric value for Scope 1 GHG emissions in "
                        "tonnes of CO2e. If not found, return null."
                    ),
                }
            },
            "required": ["scope1_value"],
        }