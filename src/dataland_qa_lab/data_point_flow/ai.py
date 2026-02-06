import asyncio
import json
import logging

from openai import AsyncAzureOpenAI

from dataland_qa_lab.data_point_flow import models
from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)
conf = config.get_config()

client = AsyncAzureOpenAI(
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
    """Executes a prompt with strict JSON enforcement and automatic retries."""
    ai_model = ai_model or conf.ai_model

    system_message = (
        "You are an AI assistant performing answer validation.\n"
        'EXPECTED JSON FORMAT: {"predicted_answer": <val>, "confidence": <float>, "reasoning": <str>, "qa_status": <str>}\n\n'
        "NULL HANDLING RULES:\n"
        "1. If data is missing or unavailable, 'predicted_answer' must be null (JSON literal, no quotes).\n"
        f"2. The 'previous_answer' provided to you is: {previous_answer}.\n"
        "3. LOGIC: If your 'predicted_answer' is null AND 'previous_answer' is null, 'qa_status' MUST BE 'QaAccepted'.\n"
        "4. LOGIC: Only use 'QaRejected' if the values represent different factual information."
    )

    user_text = (
        f"Validation Task: {prompt}\n\n"
        f"Previous Answer to compare against: {previous_answer}\n\n"
        "Definitions:\n"
        "- QaAccepted: predicted_answer matches previous_answer exactly.\n"
        "- QaRejected: predicted_answer does NOT match previous_answer.\n"
        "- QaInconclusive: insufficient evidence.\n"
    )

    content = [{"type": "text", "text": user_text}]
    if images:
        content.extend(
            [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}", "detail": "high"}}
                for img in images
            ]
        )

    try:
        response = await client.chat.completions.create(
            model=ai_model,
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": content}],
            response_format={"type": "json_object"},
            temperature=1 if "gpt-5" in ai_model else 0,
            timeout=200 if images else None,
        )

        raw_content = response.choices[0].message.content
        if not raw_content:
            msg = "Empty response from AI"
            raise ValueError(msg)  # noqa: TRY301

        data = json.loads(raw_content)

        valid_keys = {"predicted_answer", "confidence", "reasoning", "qa_status"}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}

        return models.AIResponse(**filtered_data)

    except Exception as e:  # noqa: BLE001
        logger.warning("Retry %d/3 after error: %s", retries, e)
        if retries > 0:
            await asyncio.sleep(1.5 * (4 - retries))
            return await execute_prompt(
                prompt=prompt, previous_answer=previous_answer, ai_model=ai_model, retries=retries - 1, images=images
            )

        return models.AIResponse(
            predicted_answer=None,
            confidence=0.0,
            reasoning=f"Failed after retries. Last error: {e}",
            qa_status="QaInconclusive",
        )
