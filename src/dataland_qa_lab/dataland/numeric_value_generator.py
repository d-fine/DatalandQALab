from dataland_qa_lab.dataland import generate_gpt_request, prompting_service


class NumericValueGenerator:
    """Extracts and stores all values of template 2 to 5 and compares them to the values in dataland."""

    @staticmethod
    def get_taxonomy_alligned_denominator() -> list:
        """Extracts information from template 2 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 2
        """
        return generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(2),
            prompting_service.PromptingService.create_sub_prompt_template2to4()
        )

    @staticmethod
    def get_taxonomy_alligned_numerator() -> list:
        """Extracts information from template 3 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 3.
        """
        return generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(3),
            prompting_service.PromptingService.create_sub_prompt_template2to4()
        )

    @staticmethod
    def get_taxonomy_eligible_not_alligned() -> list:
        """Extracts information from template 4 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 4.
        """
        return generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(4),
            prompting_service.PromptingService.create_sub_prompt_template2to4()
        )

    @staticmethod
    def get_taxonomy_non_eligible() -> list:
        """Extracts information from template 5 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 5.
        """
        return generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(5),
            prompting_service.PromptingService.create_sub_prompt_template5()
        )
