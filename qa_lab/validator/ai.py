import json
import logging
import sys

from openai import AzureOpenAI

from qa_lab.utils.config import get_config

logger = logging.getLogger(__name__)
config = get_config()

client = AzureOpenAI(
    api_key=config.azure_openai_api_key,
    api_version="2024-07-01-preview",
    azure_endpoint=config.azure_openai_endpoint,
)


def execute_prompt(prompt: str, ai_model: str = "gpt-4o") -> dict:
    """Sends a prompt to the AI model and returns the response."""
    prompt += '\n\n It is absolutely crucial to use the following format when answering: {"answer": <your answer, only using the data type defined in the prompt>, "confidence": <a confidence score between 0 and 1 as a float>, "reasoning": <your reasoning for the answer>}'  # noqa: E501
    response = client.chat.completions.create(
        model=ai_model,
        temperature=0,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    if not response.choices[0].message.content:
        logger.error("No content returned from AI model.")
        sys.exit(1)

    return json.loads(response.choices[0].message.content)
