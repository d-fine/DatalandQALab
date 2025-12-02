import re

from dataland_qa_lab.prompting_services import prompting_service
from dataland_qa_lab.review import generate_gpt_request


class NumericValueGenerator:
    """Extracts and stores all values of template 2 to 5 and compares them to the values in dataland."""

    TEMPLATE_ID_5 = 5

    @staticmethod
    def get_taxonomy_aligned_denominator(readable_text: str, kpi: str, ai_model: str | None = None) -> list:  # noqa: ARG004
        """Extracts information from template 2 using Azure OpenAI and returns a list of results."""
        return NumericValueGenerator.extract_values_from_template(2, readable_text, kpi)

    @staticmethod
    def get_taxonomy_aligned_numerator(readable_text: str, kpi: str, ai_model: str | None = None) -> list:  # noqa: ARG004
        """Extracts information from template 3 using Azure OpenAI and returns a list of results."""
        return NumericValueGenerator.extract_values_from_template(3, readable_text, kpi)

    @staticmethod
    def get_taxonomy_eligible_not_alligned(readable_text: str, kpi: str, ai_model: str | None = None) -> list:  # noqa: ARG004
        """Extracts information from template 4 using Azure OpenAI and returns a list of results."""
        return NumericValueGenerator.extract_values_from_template(4, readable_text, kpi)

    @staticmethod
    def get_taxonomy_non_eligible(readable_text: str, kpi: str, ai_model: str | None = None) -> list:  # noqa: ARG004
        """Extracts information from template 5 using Azure OpenAI and returns a list of results."""
        return NumericValueGenerator.extract_values_from_template(5, readable_text, kpi)

    @staticmethod
    def extract_values_from_template(
        template_id: int,
        readable_text: str,
        kpi: str,
    ) -> list:
        """Generic method to extract values from a given template using Azure OpenAI."""
        try:
            prompt_method = (
                prompting_service.PromptingService.create_sub_prompt_template5
                if template_id == NumericValueGenerator.TEMPLATE_ID_5
                else prompting_service.PromptingService.create_sub_prompt_template2to4
            )

            main_prompt = prompting_service.PromptingService.create_main_prompt(template_id, readable_text, kpi)
            sub_prompt = prompt_method(kpi)

            values = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
                main_prompt,
                sub_prompt,
            )

            if not values:
                msg = f"No results returned from GPT for template {template_id} values."
                NumericValueGenerator.throw_error(msg)

            return NumericValueGenerator.convert_to_float(values, template_id)
        except ValueError as e:
            msg = f"Error extracting values from template {template_id}: {e}"
            raise ValueError(msg) from e

    @staticmethod
    def throw_error(msg: str) -> ValueError:
        """Raises a ValueError with the given message."""
        raise ValueError(msg)

    @staticmethod
    def convert_to_float(values: list, template_id: int) -> list:
        """Converts extracted values to floats."""
        try:
            return [NumericValueGenerator.extract_number(value) for value in values]
        except Exception as e:
            msg = f"Unexpected error during float conversion for template {template_id}: {e}"
            raise ValueError(msg) from e

    @staticmethod
    def extract_number(value: str) -> float:
        """Extracts the first numeric part from a string and converts it to a float.

        Rejects -1 and handles Unicode minus signs (U+2212, U+2013).
        """
        if isinstance(value, float | int):
            num = float(value)
            # Reject value -1
            if num == -1.0:
                return None
            return num
        # Normalize Unicode minus variants to ASCII "-"
        normalized_value = (
            value.replace("\u2212", "-")  # mathematical minus (U+2212)
            .replace("\u2013", "-")  # en dash / Gedankenstrich (U+2013)
            .strip()  # remove surrounding spaces
        )
        # Safe regex: Match optional negative sign, then digits, optional dot, and more digits
        match = re.search(r"-?\d+(?:\.\d+)?", normalized_value)
        if match:
            num = float(match.group(0))
            # Reject value -1
            if num == -1.0:
                return None
            return num

        msg = f"Could not extract a valid number from '{value}'"
        raise ValueError(msg)
