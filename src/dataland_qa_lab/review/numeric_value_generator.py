import logging

from azure.ai.documentintelligence.models import AnalyzeResult

from dataland_qa_lab.prompting_services import prompting_service
from dataland_qa_lab.review import generate_gpt_request

logger = logging.getLogger(__name__)


class NumericValueGenerator:
    """Extracts and stores all values of template 2 to 5 and compares them to the values in dataland."""

    @staticmethod
    def get_taxonomy_alligned_denominator(readable_text: AnalyzeResult, kpi: str) -> list:
        """Extracts information from template 2 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list of extracted and converted float values from template 2.
        """
        try:
            # Generate GPT request
            dominator_values = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
                prompting_service.PromptingService.create_main_prompt(2, readable_text, kpi),
                prompting_service.PromptingService.create_sub_prompt_template2to4(kpi),
            )
            # Check if the GPT response is empty
            if not dominator_values:
                logger.warning("Denominator values are empty. No results returned from GPT.")
                msg = "No results returned from GPT for denominator values."
                raise ValueError(msg)  # noqa: TRY301
            # Convert the results to floats
            try:
                float_results = [float(value) for value in dominator_values]
            except Exception as e:
                logger.critical(f"Unexpected error during float conversion: {e}")  # noqa: G004
                msg = f"Unexpected error during float conversion: {e}"
                raise ValueError(msg) from e
            return float_results  # noqa: TRY300
        except ValueError as e:
            logger.critical("Unexpected error in generate_gpt_request: %s", e)
            msg = f"Error extracting values from template 2: {e}"
            raise ValueError(msg) from e

    @staticmethod
    def get_taxonomy_alligned_numerator(readable_text: AnalyzeResult, kpi: str) -> list:
        """Extracts information from template 3 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list of extracted and converted float values from template 3.
        """
        try:
            # Generate GPT request
            numerator_values = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
                prompting_service.PromptingService.create_main_prompt(3, readable_text, kpi),
                prompting_service.PromptingService.create_sub_prompt_template2to4(kpi),
            )
            # Check if the GPT response is empty
            if not numerator_values:
                logger.warning("Denominator values are empty. No results returned from GPT.")
                msg = "No results returned from GPT for denominator values."
                raise ValueError(msg)  # noqa: TRY301
            # Convert the results to floats
            try:
                float_results = [float(value) for value in numerator_values]
            except Exception as e:
                logger.critical(f"Unexpected error during float conversion: {e}")  # noqa: G004
                msg = f"Unexpected error during float conversion: {e}"
                raise ValueError(msg) from e
            return float_results  # noqa: TRY300
        except ValueError as e:
            logger.critical("Unexpected error in generate_gpt_request: %s", e)
            msg = f"Error extracting values from template 3: {e}"
            raise ValueError(msg) from e

    @staticmethod
    def get_taxonomy_eligible_not_alligned(readable_text: AnalyzeResult, kpi: str) -> list:
        """Extracts information from template 4 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 4.
        """
        try:
            # Generate GPT request
            eligible_values = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
                prompting_service.PromptingService.create_main_prompt(4, readable_text, kpi),
                prompting_service.PromptingService.create_sub_prompt_template2to4(kpi),
            )
            # Check if the GPT response is empty
            if not eligible_values:
                logger.warning("Denominator values are empty. No results returned from GPT.")
                msg = "No results returned from GPT for denominator values."
                raise ValueError(msg)  # noqa: TRY301
            # Convert the results to floats
            try:
                float_results = [float(value) for value in eligible_values]
            except Exception as e:
                logger.critical(f"Unexpected error during float conversion: {e}")  # noqa: G004
                msg = f"Unexpected error during float conversion: {e}"
                raise ValueError(msg) from e
            return float_results  # noqa: TRY300
        except ValueError as e:
            logger.critical("Unexpected error in generate_gpt_request: %s", e)
            msg = f"Error extracting values from template 4: {e}"
            raise ValueError(msg) from e

    @staticmethod
    def get_taxonomy_non_eligible(readable_text: AnalyzeResult, kpi: str) -> list:
        """Extracts information from template 5 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the extracted values of template 5.
        """
        try:
            # Generate GPT request
            non_eligible_values = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
                prompting_service.PromptingService.create_main_prompt(5, readable_text, kpi),
                prompting_service.PromptingService.create_sub_prompt_template5(kpi),
            )
            # Check if the GPT response is empty
            if not non_eligible_values:
                logger.warning("Denominator values are empty. No results returned from GPT.")
                msg = "No results returned from GPT for denominator values."
                raise ValueError(msg)  # noqa: TRY301
            # Convert the results to floats
            try:
                float_results = [float(value) for value in non_eligible_values]
            except Exception as e:
                logger.critical(f"Unexpected error during float conversion: {e}")  # noqa: G004
                msg = f"Unexpected error during float conversion: {e}"
                raise ValueError(msg) from e
            return float_results  # noqa: TRY300
        except ValueError as e:
            logger.critical("Unexpected error in generate_gpt_request: %s", e)
            msg = f"Error extracting values from template 5: {e}"
            raise ValueError(msg) from e
