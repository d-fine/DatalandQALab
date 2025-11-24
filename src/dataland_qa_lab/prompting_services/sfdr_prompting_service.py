class SFDRPromptingService:
    """Service for handling SFDR prompt requests with clear, rule-based instructions."""

    @staticmethod
    def create_scope1_prompt(markdown_text: str) -> str:
        """Creates a precise prompt for Scope 1 GHG extraction."""
        return f"""
        You are an expert ESG Data Auditor.
        Task: Extract the exact numeric value for "Scope 1 GHG Emissions" (Direct Emissions).

        TARGET UNIT: tonnes of CO2 equivalent (tCO2e).

        INSTRUCTIONS:
        1. **Locate the Value:** Find the Scope 1 emission value for the reporting year.
        2. **Check the Unit:** Identify the unit explicitly stated in the text or table header.
        3. **Normalize to Tonnes:**
           - If unit is 'kilotonnes' (kt) or 'thousands': Multiply value by 1,000.
           - If unit is 'million tonnes' (Mt) or 'millions': Multiply value by 1,000,000.
           - If unit is 'tonnes': Use value as is.

        DATA RULES:
        - **Actuals ONLY:** Extract reported data (e.g., "2023"). IGNORE targets, goals, or baseline years.
        - **Scope:** Look for "Scope 1" or "Direct emissions".
        - **Gross vs Net:** Extract GROSS emissions. Ignore "net" or "offset" values unless only those are available.
        - **Format:** Return the final calculated number as a float (e.g. 15000.0). No commas.

        RELEVANT DOCUMENT CONTEXT:
        {markdown_text}
        """

    @staticmethod
    def create_scope1_schema() -> dict:
        return SFDRPromptingService.create_generic_numeric_schema("scope1_value")

    @staticmethod
    def create_generic_numeric_prompt(kpi_name: str, unit: str, markdown_text: str) -> str:
        """Creates a strict rule-based prompt for generic numeric extraction."""
        return f"""
        You are an expert ESG Data Auditor.
        Task: Extract the numeric value for "{kpi_name}".

        TARGET UNIT: {unit}

        INSTRUCTIONS:
        1. Find the value for "{kpi_name}" in the text.
        2. Verify the unit in the text (look for headers like 'in thousands', 'MWh', '%', etc.).
        3. If the text unit differs from the Target Unit ({unit}), APPLY CONVERSION:
           - 'k' / 'kilo' / 'thousand' -> Multiply by 1,000.
           - 'M' / 'Mega' / 'million' -> Multiply by 1,000,000.
           - 'G' / 'Giga' -> Multiply by 1,000 (if target is Mega).
           - '%' -> Return as number 0-100.

        RULES:
        - Ignore future targets ("Target 2030"). Extract only the reporting year value.
        - Return strictly the numeric value (float).
        - Do not make any assumptions or estimations.
        - If the value is not found, return None.

        RELEVANT DOCUMENT CONTEXT:
        {markdown_text}
        """

    @staticmethod
    def create_generic_numeric_schema(field_id: str) -> dict:
        """Creates a schema that asks for reasoning (Chain-of-Thought) to improve accuracy."""
        return {
            "type": "object",
            "properties": {
                "unit_found_in_text": {
                    "type": "string",
                    "description": "The unit string exactly as found in the text (e.g., 'kt', 'tCO2e', 'thousand').",
                },
                "conversion_logic": {
                    "type": "string",
                    "description": "Explain your calculation. E.g., 'Found 50 kt. Target is tonnes. 50 * 1000 = 50000'.",
                },
                field_id: {
                    "type": "number",
                    "description": "The final value converted to the target unit. Return None if not found.",
                },
            },
            "required": ["unit_found_in_text", "conversion_logic", field_id],
        }