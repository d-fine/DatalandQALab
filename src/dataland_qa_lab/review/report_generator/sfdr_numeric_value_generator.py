import logging
import re
from typing import List, Any

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
        """Extracts ANY numeric value based on name and unit."""
        try:
            prompt = SFDRPromptingService.create_generic_numeric_prompt(kpi_name, unit, readable_text)
            print(prompt)
            schema = SFDRPromptingService.create_generic_numeric_schema("extracted_value")

            values = GenerateGptRequest.generate_gpt_request(prompt, schema, ai_model=ai_model)

            if not values:
                logger.warning("GPT returned no values for %s", kpi_name)
                return None

            numeric_value = SFDRNumericValueGenerator._find_numeric_value_in_list(values)

            if numeric_value is None:
                logger.warning("No numeric value found in GPT response for %s", kpi_name)
                return None

            return SFDRNumericValueGenerator.extract_number(str(numeric_value))

        except Exception as e:
            logger.exception("Error extracting %s: %s", kpi_name, e)

            return None

    @staticmethod
    def _find_numeric_value_in_list(values: List[Any]) -> Any | None:
        """Helper to find the first int/float in the list, skipping explanation strings."""
        for val in values:
            # GPT gibt Zahlen oft direkt als float/int zurück
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                return val
            # Manchmal als String wie "15000.0"
            if isinstance(val, str):
                # Wir überspringen Texte wie "Die Einheit ist Tonnen"
                # Wir suchen nach reinen Zahlen (optional mit Minus und Dezimalpunkt)
                clean_val = val.replace(",", "").strip()
                if re.match(r"^-?\d+(\.\d+)?$", clean_val):
                     return val
        return None

    @staticmethod
    def extract_number(value: str) -> float:
        if isinstance(value, float | int):
            return float(value)

        clean_value = value.replace(",", "")

        match = re.search(r"-?\d+(?:\.\d+)?", clean_value)
        if match:
            return float(match.group(0))

        msg = f"Could not extract number from '{value}'"
        raise ValueError(msg)
