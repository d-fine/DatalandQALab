class SFDRPromptingService:
    """Service for handling SFDR prompt requests with enhanced precision regarding units."""

    @staticmethod
    def create_scope1_prompt(markdown_text: str) -> str:
        """Creates a highly specialized prompt for Scope 1 GHG extraction with strict unit handling."""
        return f"""
        You are a specialist ESG Data Auditor. Your task is to extract the exact numeric value for "Scope 1 GHG Emissions" (Direct Emissions).

        Target Unit: tonnes of CO2 equivalent (tCO2e).

        ### UNIT NORMALIZATION RULES (CRITICAL):
        1. **Check the unit carefully:** Look for headers saying "in thousands", "in millions", "kt", "Mt", etc.
        2. **Convert to Target Unit (tonnes):**
           - If the text says "13.51 kt" (kilotonnes) -> Calculate 13.51 * 1,000 -> Return 13510.0
           - If the text says "13.51 thousand tonnes" -> Calculate 13.51 * 1,000 -> Return 13510.0
           - If the text says "1.5 Mt" (million tonnes) -> Calculate 1.5 * 1,000,000 -> Return 1500000.0
           - If the text says "13,510 tonnes" -> Return 13510.0
        
        ### EXTRACTION RULES:
        - **Actuals ONLY:** Extract historical data (e.g., "2023"). IGNORE targets or goals.
        - **Gross vs. Net:** Extract **GROSS** emissions (market-based preferred if available, otherwise location-based).
        - **Consolidation:** Extract the global group-wide total.
        - **Format:** Return ONLY the raw float number (e.g. 13510.0). Do not use comma separators for thousands.

        ### DOCUMENT CONTEXT:
        {markdown_text}
        """

    @staticmethod
    def create_scope1_schema() -> dict:
        return SFDRPromptingService.create_generic_numeric_schema("scope1_value")

    @staticmethod
    def create_generic_numeric_prompt(kpi_name: str, unit: str, markdown_text: str) -> str:
        """Creates a robust generic prompt that handles unit conversion."""
        return f"""
        You are a meticulous ESG Data Auditor. Extract the precise numeric value for: "{kpi_name}".

        Target Unit: {unit}

        ### STRICT RULES:
        1. **Unit Conversion is MANDATORY:**
           - Verify if the value in the text is scaled (e.g., "in thousands", "in millions", "kt", "MWh", "GWh").
           - **You MUST calculate** the final value in the Target Unit ({unit}).
           - Example: If Target is 'tonnes' and text is '10 kt', return 10000.0.
        2. **Identify Actuals:** Extract only realized historical performance (e.g., reporting year). Ignore targets/goals.
        3. **Precision:** If the text matches the target unit exactly, return the number as is.
        4. **Output Format:** Return ONLY the final calculated float (e.g. 12345.0). No commas.
        5. **Not Found:** If specific data is missing or ambiguous, return None. Do not guess.

        ### DOCUMENT CONTEXT:
        {markdown_text}
        """

    @staticmethod
    def create_generic_numeric_schema(field_id: str) -> dict:
        """Creates a schema that includes reasoning to force the AI to think about units."""
        return {
            "type": "object",
            "properties": {
                "unit_found_in_text": {
                    "type": "string",
                    "description": "The exact unit string found in the document (e.g., 'thousand tonnes', 'kt', 'tCO2e')."
                },
                "conversion_logic": {
                    "type": "string",
                    "description": "Explanation of any conversion performed (e.g., 'Value was in kt, so I multiplied by 1000')."
                },
                field_id: {
                    "type": "number",
                    "description": f"The final extracted value converted to the target unit. If not found, return None.",
                }
            },
            "required": ["unit_found_in_text", "conversion_logic", field_id],
        }