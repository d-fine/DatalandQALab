class SFDRPromptingService:
    """Service for handling SFDR prompt requests."""

    @staticmethod
    def create_scope1_prompt(markdown_text: str) -> str:
        """Legacy prompt (keep for compatibility)."""
        return f"""
        You are an ESG analyst. Extract "Scope 1 GHG emissions".
        Unit: tonnes of CO2e.
        Return ONLY the number as float (e.g. 15000.0) or -1 if not found.
        # relevant documents
        {markdown_text}
        """

    @staticmethod
    def create_scope1_schema() -> dict:
        return SFDRPromptingService.create_generic_numeric_schema("scope1_value")

    @staticmethod
    def create_generic_numeric_prompt(kpi_name: str, unit: str, markdown_text: str) -> str:
        """Creates a generic prompt for ANY numeric SFDR KPI."""
        return f"""
        You are an ESG analyst. From the given text, extract the numeric value for: "{kpi_name}".
        
        Rules:
        - Look strictly for this specific KPI.
        - The unit must be compatible with: {unit}.
        - Return ONLY the number as a float (e.g., 123.45).
        - If not found, return -1.
        
        # relevant documents
        {markdown_text}
        """

    @staticmethod
    def create_generic_numeric_schema(field_id: str) -> dict:
        """Creates a generic schema for numeric extraction."""
        return {
            "type": "object",
            "properties": {
                field_id: {
                    "type": "number",
                    "description": f"Extracted numeric value for {field_id}. If not found, return -1.",
                }
            },
            "required": [field_id],
        }
