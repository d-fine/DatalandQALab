from azure.ai.documentintelligence.models import AnalyzeResult

from dataland_qa_lab.prompting_services import prompting_service
from dataland_qa_lab.review import generate_gpt_request


class NumericValueGenerator:
    """Extracts and stores all values of template 2 to 5 and compares them to the values in dataland."""

    @staticmethod
    def get_taxonomy_alligned_denominator(readable_text: AnalyzeResult) -> list:
        """Extracts information from template 2 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 2
        """
        dominator_values = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(2, readable_text),
            prompting_service.PromptingService.create_sub_prompt_template2to4(),
        )
        float_results = [float(value) for value in dominator_values]
        return float_results

    @staticmethod
    def get_taxonomy_alligned_numerator(readable_text: AnalyzeResult) -> list:
        """Extracts information from template 3 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 3.
        """
        numerator_values = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(3, readable_text),
            prompting_service.PromptingService.create_sub_prompt_template2to4(),
        )
        float_results = [float(value) for value in numerator_values]
        return float_results

    @staticmethod
    def get_taxonomy_eligible_not_alligned(readable_text: AnalyzeResult) -> list:
        """Extracts information from template 4 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 4.
        """
        eligible_values = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(4, readable_text),
            prompting_service.PromptingService.create_sub_prompt_template2to4(),
        )
        float_results = [float(value) for value in eligible_values]
        return float_results

    @staticmethod
    def get_taxonomy_non_eligible(readable_text: AnalyzeResult) -> list:
        """Extracts information from template 5 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the extracted values of template 5.
        """
        non_eligible_values = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(5, readable_text),
            prompting_service.PromptingService.create_sub_prompt_template5(),
        )
        float_results = [float(value) for value in non_eligible_values]
        return float_results
