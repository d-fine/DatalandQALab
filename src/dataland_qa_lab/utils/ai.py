import asyncio
import json
import logging

from openai import AzureOpenAI

from dataland_qa_lab.models import data_point_flow
from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)
conf = config.get_config()

client = AzureOpenAI(
    api_key=conf.azure_openai_api_key,
    api_version="2024-07-01-preview",
    azure_endpoint=conf.azure_openai_endpoint,
)


async def execute_prompt(prompt: str, ai_model: str | None = None, retries: int = 3) -> data_point_flow.AIResponse:
    logger.info("Executing prompt with AI model: %s", ai_model)
    """Sends a prompt to the AI model and returns the response."""
    prompt += """\n\nYou are an AI assistant. You must answer the user's question strictly in **valid JSON format**, following exactly this structure:

{
    "predicted_answer": <your answer using only the data type specified in the user's prompt>,
    "confidence": <a float between 0 and 1>,
    "reasoning": <your reasoning as a string>
}

Rules you must follow:

1. Your **entire output** must be exactly one JSON dictionary as shown above.
2. Do **not** include any text, explanation, code blocks, example JSON, or formatting outside of the dictionary.
3. All strings and keys must use double quotes. The output must be valid JSON parsable by `json.loads`.
4. Any deviation from this structure, including extra text or symbols, will be considered invalid and rejected.
5. Only provide data that strictly fits the types specified by the user's query.

6. Output must be machine-parsable JSON only. No human-readable explanations, no code fences, no examples. If you fail, output {"predicted_answer": null, "confidence": 0.0, "reasoning": "Formatting error prevented valid JSON output."}

"""  # noqa: E501
    if not ai_model:
        ai_model = conf.ai_model

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=ai_model,
            temperature=1 if "gpt-5" in ai_model else 0,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
    except Exception as e:
        logger.error("Error while calling AI model: %s. Retries left: %d", str(e), retries)
        if retries > 0:
            return await execute_prompt(prompt, ai_model, retries - 1)
        return data_point_flow.AIResponse(
            predicted_answer=None, confidence=0.0, reasoning="Error calling AI model: " + str(e)
        )

    if not response.choices[0].message.content:
        logger.error("No content returned from AI model. Retries left: %d", retries)
        if retries > 0:
            return await execute_prompt(prompt, ai_model, retries - 1)
        return data_point_flow.AIResponse(
            predicted_answer=None, confidence=0.0, reasoning="No content returned from AI model."
        )
    try:
        return data_point_flow.AIResponse(**json.loads(response.choices[0].message.content))
    except json.JSONDecodeError:
        if retries > 0:
            logger.warning("Failed to parse AI response as JSON. Retrying... (%d retries left)", retries)
            return await execute_prompt(prompt, ai_model, retries - 1)
        return data_point_flow.AIResponse(predicted_answer=None, confidence=0.0, reasoning="Couldn't parse response.")
