import asyncio
import json
import logging

from openai import AzureOpenAI

from dataland_qa_lab.data_point_flow import models
from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)
conf = config.get_config()

client = AzureOpenAI(
    api_key=conf.azure_openai_api_key,
    api_version="2024-07-01-preview",
    azure_endpoint=conf.azure_openai_endpoint,
)


async def execute_prompt(  # noqa: PLR0911
    prompt: str,
    previous_answer: str,
    ai_model: str | None = None,
    retries: int = 3,
    images: list[str] | None = None,
) -> models.AIResponse:
    """Executes a prompt using the specified AI model and returns the AIResponse."""
    logger.info("Executing prompt with AI model: %s", ai_model)
    full_prompt = (
        f"{prompt}\n\n"
        "You are an AI assistant performing answer validation.\n\n"
        "Your task is to produce **exactly one valid JSON object** with the structure below. "
        "The output must be parsable by `json.loads` without any modification.\n\n"
        "Required JSON structure:\n"
        "{\n"
        '  "predicted_answer": <answer using ONLY the data type explicitly required in the user prompt>,\n'
        '  "confidence": <float between 0.0 and 1.0>,\n'
        '  "reasoning": <string explaining how you derived the predicted_answer>,\n'
        '  "qa_status": <string: "ACCEPTED", "REJECTED", or "INCONCLUSIVE">\n'
        "}\n\n"
        "Definitions:\n"
        "- ACCEPTED: predicted_answer matches previous_answer exactly.\n"
        "- REJECTED: predicted_answer does NOT match previous_answer.\n"
        "- INCONCLUSIVE: predicted_answer does not match previous_answer AND there is insufficient evidence to determine the correct answer.\n\n"  # noqa: E501
        f"previous_answer to compare against: {previous_answer}\n\n"
        "STRICT RULES (must follow all):\n"
        "1. Output ONLY the JSON object — no additional text, no explanations, no markdown, no code blocks.\n"
        "2. Use double quotes for all JSON keys and string values.\n"
        "3. Do NOT include trailing commas.\n"
        "4. Do NOT include comments.\n"
        "5. Ensure the output is valid JSON and machine-readable.\n"
        "6. If you are unable to comply for ANY reason, output EXACTLY this fallback JSON:\n"
        '{"predicted_answer": null, "confidence": 0.0, '
        '"reasoning": "Formatting error prevented valid JSON output.", "qa_status": "INCONCLUSIVE"}'
    )

    if not ai_model:
        ai_model = conf.ai_model

    if images:
        content = [{"type": "text", "text": full_prompt}]
        content.extend(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}",
                    "detail": "high",
                },
            }
            for img_base64 in images
        )
        messages = [{"role": "user", "content": content}]
        call_timeout = 200
    else:
        messages = [{"role": "user", "content": full_prompt}]
        call_timeout = None

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=ai_model,
            temperature=1 if "gpt-5" in ai_model else 0,
            messages=messages,
            timeout=call_timeout,
        )
    except Exception as e:
        logger.exception("Error while calling AI model: %s. Retries left: %d", str(e), retries)  # noqa: RUF065, TRY401
        if retries > 0:
            return await execute_prompt(
                prompt=prompt, previous_answer=previous_answer, ai_model=ai_model, retries=retries - 1, images=images
            )
        return models.AIResponse(
            predicted_answer=None,
            confidence=0.0,
            reasoning="Error calling AI model: " + str(e),
            qa_status="INCONCLUSIVE",
        )

    if not response.choices[0].message.content:
        logger.error("No content returned from AI model. Retries left: %d", retries)
        if retries > 0:
            return await execute_prompt(
                prompt=prompt, previous_answer=previous_answer, ai_model=ai_model, retries=retries - 1, images=images
            )
        return models.AIResponse(
            predicted_answer=None,
            confidence=0.0,
            reasoning="No content returned from AI model.",
            qa_status="INCONCLUSIVE",
        )
    try:
        return models.AIResponse(**json.loads(response.choices[0].message.content))
    except json.JSONDecodeError:
        if retries > 0:
            logger.warning("Failed to parse AI response as JSON. Retrying... (%d retries left)", retries)
            return await execute_prompt(
                prompt=prompt, previous_answer=previous_answer, ai_model=ai_model, retries=retries - 1, images=images
            )
        return models.AIResponse(
            predicted_answer=None, confidence=0.0, reasoning="Couldn't parse response.", qa_status="INCONCLUSIVE"
        )
