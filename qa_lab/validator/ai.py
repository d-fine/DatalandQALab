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
    prompt += (
        "\n\nYou must answer **strictly** in valid JSON format as a single dictionary, with no "
        "extra symbols, text, or formatting. The dictionary must follow exactly this structure: "
        '{"answer": <your answer using only the data type specified in the prompt>, '
        '"confidence": <a float between 0 and 1>, '
        '"reasoning": <your reasoning as a string>}. '
        "Do not include anything else. Your output will be parsed by json.loads, so it must be "
        "syntactically correct JSON with double quotes for all strings and keys. "
        "Any deviation will be considered invalid."
    )

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
