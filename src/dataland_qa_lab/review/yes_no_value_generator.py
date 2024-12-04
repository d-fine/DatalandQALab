from azure.ai.documentintelligence.models import AnalyzeResult
from openai import AzureOpenAI

from dataland_qa_lab.utils import config


class YesNoValueGenerator:
    """Class to provide logic to get correct yes and no values of company report."""

    def __init__(self) -> None:
        """Extract the sections 426 to 431."""
        self.conf = config.get_config()

    def extract_section_426(self, relevant_document: AnalyzeResult) -> str | None:
        """Get values from yes and no section."""
        client = AzureOpenAI(
            api_key=self.conf.azure_openai_api_key, api_version="2024-07-01-preview",
            azure_endpoint=self.conf.azure_openai_endpoint
        )

        deployment_name = "gpt-4o"

        prompt = f"""
        Answer only with 'yes' or 'no'!
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
        Given the information from the [relevant documents], is the company engaged in the research, development,
        demonstration, and deployment of innovative power generation facilities that generate energy from nuclear
        processes with minimal waste from the fuel cycle, finance such activities, or hold risk positions related
        to these activities? Just answer the question with yes or no. The answer should not be longer than 3
        characters, should not include punctation and start with a capital letter.

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
        return initial_openai_response.choices[0].message.content
