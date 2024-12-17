import json

from azure.ai.documentintelligence.models import AnalyzeResult
from openai import AzureOpenAI

from dataland_qa_lab.dataland.dataset_provider import get_dataset_by_id
from dataland_qa_lab.pages.pages_provider import get_relevant_pages_of_pdf
from dataland_qa_lab.pages.text_to_doc_intelligence import extract_text_of_pdf
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def extract_denomitor_template(relevant_document: AnalyzeResult) -> dict:
    """Get values from denomitor."""
    conf = config.get_config()
    client = AzureOpenAI(
        api_key=conf.azure_openai_api_key,
        api_version="2024-07-01-preview",
        azure_endpoint=conf.azure_openai_endpoint,
    )
    deployment_name = "gpt-4o"
    prompt = get_prompt(relevant_document)
    initial_openai_response = client.chat.completions.create(
    model=deployment_name,
    temperature=0,
    messages=[
        {"role": "system", "content": prompt},
    ],
    tool_choice="required",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "requested_information_precisely_found_in_relevant_documents",
                "description": "Submit the requested information. "
                "Use this function when the information is precisely stated in the relevant documents. ",
                "parameters": generate_schema_tmeplate5([1, 2, 3, 4, 5, 6, 7, 8]),
            },
        }
    ],
)
    response = initial_openai_response.choices[0].message.tool_calls[0].function
    repsonse_arugments = json.loads(response.arguments)
    response_dict = convert_rows_to_taxonomy(repsonse_arugments)
    print(response_dict)


def convert_rows_to_taxonomy(data) -> dict:
    """Converts row-based data into the required taxonomy dictionary format."""
    # Define the mapping for rows to the taxonomy keys
    row_mapping = {
        "row1": "taxonomy_non_eligible_share_n_and_g426",
        "row2": "taxonomy_non_eligible_share_n_and_g427",
        "row3": "taxonomy_non_eligible_share_n_and_g428",
        "row4": "taxonomy_non_eligible_share_n_and_g429",
        "row5": "taxonomy_non_eligible_share_n_and_g430",
        "row6": "taxonomy_non_eligible_share_n_and_g431",
        "row7": "taxonomy_non_eligible_share_other_activities",
        "row8": "taxonomy_non_eligible_share"
    }

    # Initialize the output dictionary
    output = {}

    # Process rows and map to taxonomy keys
    for row, key in row_mapping.items():
        value_key = f"answer_value_%_{row}"
        value = data.get(value_key, None)  # Fetch the row value, default to None
        output[key] = value
    return output


def generate_schema_tmeplate5(rows: list) -> dict:
    """Generates a schema for the given rows.

    Args:
        rows (list): A list of row numbers.

    Returns:
        dict: A dictionary representing the schema.
    """
    schema = {"type": "object", "properties": {}, "required": []}

    # Für jede Zeile Felder hinzufügen
    for row in rows:
        for metric, value_type in [("€", "number"), ("%", "number")]:
            value_key = f"answer_value_{metric}_row{row}"
            currency_key = f"answer_currency_{metric}_row{row}"

            schema["properties"][value_key] = {
                "type": value_type,
                "description": f"""The precise answer to the {metric} of row {row}
                without any thousand separators."""
                if metric == "€"
                else f"The precise answer to the percentage of row {row}.",
            }
            schema["properties"][currency_key] = {
                "type": "string",
                "description": f"""The currency of the answer to the {metric} of row {row}
                (e.g. €, $, Mio.€, Mio.$, M$, € in thousends)"""
                if metric == "€"
                else "%",
            }

            schema["required"].extend([value_key, currency_key])

    return schema


def get_prompt(relevant_document: AnalyzeResult) -> str:
    """Generates a prompt for the AI model based on the relevant document."""
    return f"""
    You are an AI research Agent. As the agent, you answer questions briefly, succinctly, and factually.
    Always justify your answer.
    # Safety
    - You **should always** reference factual statements to search results based on [relevant_document]
    - Search results based on [relevant_document] may be incomplete or irrelevant. You do not make assumptions
    on the search results beyond strictly what's returned.
    - If the search results based on [relevant_document] do not contain sufficient information to answer user
    message completely, you respond using the tool 'cannot_answer_question'.
    - Your responses should avoid being vague, controversial, or off-topic.
    # Task
    For each row 1-8 of template 5 (revenue) it's called
    "Taxonomy non-eligible economic activities",
    give me one value and one percentage per row.
    Focus on the row numbers on the left side of the table.
    If you can't find the value, write null.
    Consider translating for this given task like Meldebogen instead of template.
    Make sure to provides the right units. Like €, Mio €, Mio, € in thousends or %.
    # Relevant Documents
    {relevant_document.content}
    """

# For testing purposes
def create_data_collection(dataset_id: str) -> NuclearAndGasDataCollection:
    dataset = get_dataset_by_id(dataset_id).data
    test_data_collection = NuclearAndGasDataCollection(dataset)
    return test_data_collection

if __name__ == "__main__":
    dataset_id = "fae59f2e-c438-4457-9a74-55c0db006fee"
    test_data_collection = create_data_collection(dataset_id)
    relevant_pages = get_relevant_pages_of_pdf(test_data_collection)
    relevant_document = extract_text_of_pdf(relevant_pages)
    extract_denomitor_template(relevant_document)