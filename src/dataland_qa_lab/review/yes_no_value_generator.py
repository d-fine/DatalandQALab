import logging

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_backend.models.yes_no import YesNo

from dataland_qa_lab.prompting_services import prompting_service
from dataland_qa_lab.review import generate_gpt_request

logger = logging.getLogger(__name__)


def get_yes_no_values_from_report(readable_text: AnalyzeResult) -> dict[str, YesNo | None]:
    """Extracts information from template 1 using Azure OpenAI and returns a list of results.

    Returns:
        list: A list including the etracted values of template 1
    """
    try:
        extracted_list = generate_gpt_request.GenerateGptRequest.generate_gpt_request(
            prompting_service.PromptingService.create_main_prompt(1, readable_text, ""),
            prompting_service.PromptingService.create_sub_prompt_template1(),
        )
        if not extracted_list:
            logger.warning("Yes_No Values are empty. No results returned from GPT.")
            msg = "No results returned from GPT for Yes_No values."
            raise ValueError(msg)  # noqa: TRY301

    except Exception as e:
        logger.critical("Unexpected error in generate_gpt_request: %s", e)
        msg = f"Error extracting values from template 1: {e}"
        raise ValueError(msg) from e

    sections = {
        "nuclear_energy_related_activities_section426": YesNo(extracted_list[0]),
        "nuclear_energy_related_activities_section427": YesNo(extracted_list[1]),
        "nuclear_energy_related_activities_section428": YesNo(extracted_list[2]),
        "fossil_gas_related_activities_section429": YesNo(extracted_list[3]),
        "fossil_gas_related_activities_section430": YesNo(extracted_list[4]),
        "fossil_gas_related_activities_section431": YesNo(extracted_list[5]),
    }

    return sections
