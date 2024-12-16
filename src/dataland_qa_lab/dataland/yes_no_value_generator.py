from dataland_qa_lab.dataland import generate_gpt_request, prompting_service


class YesNoValueGenerator:
    """Extracts and stores all values of template 1 and compares them to the values in dataland."""

    @staticmethod
    def get_correct_values_from_report() -> list:
        """Extracts information from template 1 using Azure OpenAI and returns a list of results.

        Returns:
            list: A list including the etracted values of template 1
        """
        return generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(1),
            prompting_service.PromptingService.create_sub_prompt_template1()
        )
