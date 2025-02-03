import logging

from dataland_backend.models.yes_no import YesNo

from dataland_qa_lab.prompting_services import prompting_service
from dataland_qa_lab.review import generate_gpt_request

logger = logging.getLogger(__name__)


NUM_EXPECTED_VALUES = 6


def get_yes_no_values_from_report(readable_text: str) -> dict[str, YesNo | None]:
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
            msg = "No results returned from GPT for Yes_No values."
            throw_error(msg)

    except (ValueError, TypeError) as e:
        msg = f"Error extracting values from template 1: {e}"
    if len(extracted_list) != NUM_EXPECTED_VALUES:
        msg = "Yes_No values are too short or too long from GPT."
        throw_error(msg)

    sections = {
        "nuclear_energy_related_activities_section426": YesNo(extracted_list[0]),
        "nuclear_energy_related_activities_section427": YesNo(extracted_list[1]),
        "nuclear_energy_related_activities_section428": YesNo(extracted_list[2]),
        "fossil_gas_related_activities_section429": YesNo(extracted_list[3]),
        "fossil_gas_related_activities_section430": YesNo(extracted_list[4]),
        "fossil_gas_related_activities_section431": YesNo(extracted_list[5]),
    }

    return sections


def throw_error(msg: str) -> ValueError:
    """Raises a ValueError with the given message."""
    raise ValueError(msg)
