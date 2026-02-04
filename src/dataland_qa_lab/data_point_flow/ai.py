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


async def execute_prompt(
    prompt: str,
    previous_answer: str,
    ai_model: str | None = None,
    retries: int = 3,
    images: list[str] | None = None,
) -> models.AIResponse:
    """Execute the AI prompt and return the response."""
    target_model = ai_model or conf.ai_model
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
        '  "qa_status": <string: "QaAccepted", "QaRejected", or "QaInconclusive">\n'
        "}\n\n"
        "Definitions:\n"
        "- QaAccepted: predicted_answer matches previous_answer exactly.\n"
        "- QaRejected: predicted_answer does NOT match previous_answer.\n"
        "- QaInconclusive: predicted_answer does not match previous_answer AND there is insufficient evidence to determine the correct answer.\n\n"  # noqa: E501
        f"previous_answer to compare against: {previous_answer}\n\n"
        "STRICT RULES (must follow all):\n"
        "1. Output ONLY the JSON object — no additional text, no explanations, no markdown, no code blocks.\n"
        "2. Use double quotes for all JSON keys and string values.\n"
        "3. Do NOT include trailing commas.\n"
        "4. Do NOT include comments.\n"
        "5. Ensure the output is valid JSON and machine-readable.\n"
        "6. If you are unable to comply for ANY reason, output EXACTLY this fallback JSON:\n"
        '{"predicted_answer": null, "confidence": 0.0, '
        '"reasoning": "Formatting error prevented valid JSON output.", "qa_status": "QaInconclusive"}'
    )

    messages = (
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": full_prompt},
                    *[
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img}",
                                "detail": "high",
                            },
                        }
                        for img in images
                    ],
                ],
            }
        ]
        if images
        else [{"role": "user", "content": full_prompt}]
    )

    call_timeout = 200 if images else None
    temperature = 1 if "gpt-5" in target_model else 0

    for attempt in range(retries + 1):
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=target_model,
                temperature=temperature,
                messages=messages,
                timeout=call_timeout,
            )

            content = response.choices[0].message.content
            if not content:
                msg = "No content returned"
                raise ValueError(msg)  # noqa: TRY301

            return models.AIResponse(**json.loads(content))

        except (Exception, json.JSONDecodeError) as e:  # noqa: BLE001
            logger.warning(
                "Attempt %d failed: %s. Retrying...",
                attempt + 1,
                str(e),  # noqa: RUF065
            )
            if attempt == retries:
                return models.AIResponse(
                    predicted_answer=None,
                    confidence=0.0,
                    reasoning=f"Execution failed after {retries} retries: {e}",
                    qa_status="QaInconclusive",
                )
    return None
