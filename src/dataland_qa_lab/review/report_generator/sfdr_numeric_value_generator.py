import logging
import re

from dataland_qa_lab.prompting_services.sfdr_prompting_service import SFDRPromptingService
from dataland_qa_lab.review.generate_gpt_request import GenerateGptRequest

logger = logging.getLogger(__name__)


class SFDRNumericValueGenerator:
    """Extracts numeric values for SFDR fields using Azure OpenAI."""

    @staticmethod
    def get_scope1_emissions(readable_text: str) -> float | None:
        """Specific method for Scope 1 (Legacy wrapper)."""
        return SFDRNumericValueGenerator.get_generic_numeric_value(
            readable_text, "Scope 1 GHG emissions", "tonnes CO2e"
        )

    @staticmethod
    def get_generic_numeric_value(
        readable_text: str, kpi_name: str, unit: str, ai_model: str = "gpt-4o"
    ) -> float | None:
        """Extracts ANY numeric value based on name and unit.

        Returns:
            float: The extracted value if found.
            None: If not found or strictly stated as not present (-1 from AI).
        """
        try:
            prompt = SFDRPromptingService.create_generic_numeric_prompt(kpi_name, unit, readable_text)
            schema = SFDRPromptingService.create_generic_numeric_schema("extracted_value")

            values = GenerateGptRequest.generate_gpt_request(prompt, schema, ai_model=ai_model)

            if not values:
                logger.warning("GPT returned no values for %s", kpi_name)
                return None

            raw_value = values[0]

            if str(raw_value) == "-1":
                return None

            return SFDRNumericValueGenerator.extract_number(str(raw_value))

        except Exception as e:
            logger.error("Error extracting %s: %s", kpi_name, e)

            return None

    @staticmethod
    def extract_number(value: str) -> float:
        if isinstance(value, float | int):
            return float(value)

        clean_value = value.replace(",", "")

        match = re.search(r"-?\d+(?:\.\d+)?", clean_value)
        if match:
            return float(match.group(0))

        raise ValueError(f"Could not extract number from '{value}'")
