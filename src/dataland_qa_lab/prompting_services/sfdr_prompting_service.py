class SFDRPromptingService:
    """Service for handling SFDR prompt requests."""

    @staticmethod
    def create_scope1_prompt(markdown_text: str) -> str:
        """Creates the main prompt for extracting Scope 1 GHG emmissions."""
        return f"""
        You are an ESG analyst. From the given text, extract the numeric value of "Scope 1 GHG emissions".
        Rules:
        - Only use information explicitly stated in the text. Do not infer or assume any values.
        - Look strictly for direct (Scope 1) greenhouse gas emissions.
        - The unit must be tonnes of CO2e (for example tCO2, metric tons and so on)
        - Ignore Scope 2 or Scope 3 data completely
        - If multiple years are reported, take the most recent one
        - return ONLY the number as a float (e.g., 12345.67), If not found, return -1
        
        Here is an Example:
        Text: "In 2023, total Scope 1 emissions amounted to 15,000 tCO2e."
        Output: 15000.0
        
        # relevant documents
        {markdown_text}
        """

    @staticmethod
    def create_scope1_schema() -> dict:
        """Generates the JSON schema for Scope 1 GHG expected output."""
        return {
            "type": "object",
            "properties": {
                "scope1_value": {
                    "type": "number",
                    "description": "Extracted numeric value for Scope 1 GHG emissions in tonnes of CO2e. If not found, return -1.",
                }
            },
            "required": ["scope1_value"],
        }
