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
        return generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(2, readable_text),
            prompting_service.PromptingService.create_sub_prompt_template2to4(),
        )

    @staticmethod
    def get_taxonomy_alligned_numerator(readable_text: AnalyzeResult) -> list:
        """Extracts information from template 3 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 3.
        """
        return generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(3, readable_text),
            prompting_service.PromptingService.create_sub_prompt_template2to4(),
        )

    @staticmethod
    def get_taxonomy_eligible_not_alligned(readable_text: AnalyzeResult) -> list:
        """Extracts information from template 4 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 4.
        """
        return generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(4, readable_text),
            prompting_service.PromptingService.create_sub_prompt_template2to4(),
        )

    @staticmethod
    def get_taxonomy_non_eligible(readable_text: AnalyzeResult) -> list:
        """Extracts information from template 5 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 5.
        """
        return generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(5, readable_text),
            prompting_service.PromptingService.create_sub_prompt_template5(),
        )
