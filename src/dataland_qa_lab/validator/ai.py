from dataland_qa_lab.utils.config import get_config

from openai import AzureOpenAI


config = get_config()

client = AzureOpenAI(
    api_key=config.azure_openai_api_key,
    api_version="2024-07-01-preview",
    azure_endpoint=config.azure_openai_endpoint,
)


def send_prompt(prompt: str, ai_model: str = "gpt-4o") -> str | None:
    """Sends a prompt to the AI model and returns the response."""
    response = client.chat.completions.create(
        model=ai_model,
        temperature=0,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content
