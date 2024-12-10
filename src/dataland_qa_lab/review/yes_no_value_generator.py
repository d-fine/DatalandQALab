import ast

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_backend.models.yes_no import YesNo
from openai import AzureOpenAI

from dataland_qa_lab.utils import config


def extract_yes_no_template(relevant_document: AnalyzeResult) -> dict[str, YesNo | None]:
    """Get values from yes and no section."""
    conf = config.get_config()
    client = AzureOpenAI(
        api_key=conf.azure_openai_api_key,
        api_version="2024-07-01-preview",
        azure_endpoint=conf.azure_openai_endpoint,
    )
    deployment_name = "gpt-4o"
    prompt = f"""
    You are an AI research Agent. As the agent, you answer questions briefly, succinctly, and factually.
    Always justify you answer.
    # Safety
    - You **should always** reference factual statements to search results based on [relevant documents]
    - Search results based on [relevant documents] may be incomplete or irrelevant. You do not make assumptions
      on the search results beyond strictly what's returned.
    - If the search results based on [relevant documents] do not contain sufficient information to answer user
      message completely, you respond using the tool 'cannot_answer_question'
    - Your responses should avoid being vague, controversial or off-topic.
    # Task
    Only answer with one word per row, either Yes or No.
    Given the information from the [relevant documents], answer the following statements with 'yes' or 'no':
    Provide every response from 1 to 6 to the statements given in [relevant documents]. The result should be
    in the format ['Yes', 'Yes', 'Yes', 'No', 'No', 'No'] with the value of the first question being the first
    element in the row.
    # Relevant Documents
    {relevant_document.content}
    """
    initial_openai_response = client.chat.completions.create(
        model=deployment_name,
        temperature=0,
        messages=[
            {"role": "system", "content": prompt},
        ],
    )
    value = initial_openai_response.choices[0].message.content
    value_list = ast.literal_eval(value)

    sections = {
        "nuclear_energy_related_activities_section426": YesNo(value_list[0]),
        "nuclear_energy_related_activities_section427": YesNo(value_list[1]),
        "nuclear_energy_related_activities_section428": YesNo(value_list[2]),
        "fossil_gas_related_activities_section429": YesNo(value_list[3]),
        "fossil_gas_related_activities_section430": YesNo(value_list[4]),
        "fossil_gas_related_activities_section431": YesNo(value_list[5]),
    }

    return sections
