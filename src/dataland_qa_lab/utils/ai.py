import json
import logging

from openai import AzureOpenAI

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)
conf = config.get_config()

client = AzureOpenAI(
    api_key=conf.azure_openai_api_key,
    api_version="2024-07-01-preview",
    azure_endpoint=conf.azure_openai_endpoint,
)


def execute_prompt(prompt: str, ai_model: str | None = None, retries: int = 3, images: list[str] | None = None) -> dict:
    """Sends a prompt to the AI model and returns the response."""
    prompt += """\n\nYou are an AI assistant. You must answer the user's question strictly in **valid JSON format**, following exactly this structure:

{
    "answer": <your answer using only the data type specified in the user's prompt>,
    "confidence": <a float between 0 and 1>,
    "reasoning": <your reasoning as a string>
}

Rules you must follow:

1. Your **entire output** must be exactly one JSON dictionary as shown above.
2. Do **not** include any text, explanation, code blocks, example JSON, or formatting outside of the dictionary.
3. All strings and keys must use double quotes. The output must be valid JSON parsable by `json.loads`.
4. Any deviation from this structure, including extra text or symbols, will be considered invalid and rejected.
5. Only provide data that strictly fits the types specified by the user's query.

6. Output must be machine-parsable JSON only. No human-readable explanations, no code fences, no examples. If you fail, output {"answer": null, "confidence": 0.0, "reasoning": "Formatting error prevented valid JSON output."}

"""  # noqa: E501
    if not ai_model:
        ai_model = conf.ai_model
    
    if images:
        content = [
            {"type": "text", "text": prompt}
        ]
        
        for img_base64 in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}",
                    "detail": conf.vision.detail_level
                }
            })
            
        logger.debug("Sending prompt with %d images to AI model %s", len(images), ai_model)
    else:
        content = prompt
        logger.debug("Sending prompt without images to AI model %s", ai_model)
        
    try:
        response = client.chat.completions.create(
            model=ai_model,
            temperature=1 if "gpt-5" in ai_model else 0,
            messages=[
                {"role": "user", "content": content}
            ],
            timeout=conf.vision.timeout if images else 60,
        )
    except Exception as e:
        logger.error("  Error during AI model call: %s. Retries left: %d", str(e), retries)
        if retries > 0:
            return execute_prompt(prompt, ai_model, retries - 1, images)
        return {"answer": None, "confidence": 0.0, "reasoning": " AI model call failed."}

    if not response.choices[0].message.content:
        logger.error("No content returned from AI model. Retries left: %d", retries)
        if retries > 0:
            return execute_prompt(prompt, ai_model, retries - 1, images)
        return {"answer": None, "confidence": 0.0, "reasoning": "No content returned from AI model."}

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        if retries > 0:
            logger.warning("Failed to parse AI response as JSON. Retrying... (%d retries left)", retries)
            return execute_prompt(prompt, ai_model, retries - 1, images)
        return {"answer": None, "confidence": 0.0, "reasoning": "Couldn't parse response."}
