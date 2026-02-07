import json
from logging import getLogger
from pathlib import Path

from dataland_qa_lab.data_point_flow import models
from dataland_qa_lab.utils import config

conf = config.get_config()
logger = getLogger(__name__)

default_prompts_dir = Path(__file__).parent.parent / "prompts"


def get_prompts(prompts_dir: Path = default_prompts_dir) -> dict:
    """Return all prompts from the prompts directory."""
    if not prompts_dir.is_dir():
        msg = f"Prompts directory not found: {prompts_dir}"
        raise FileNotFoundError(msg)

    combined = {}
    for file in prompts_dir.glob("*.json"):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                combined.update(data)
            else:
                logger.error("JSON file %s must be a dictionary object.", file.name)
        except json.JSONDecodeError:
            logger.exception("Failed to decode JSON from %s", file.name)

    return combined


def get_prompt_config(data_point_type: str) -> models.DataPointPrompt | None:
    """Retrieve the validation prompt or return None if not found."""
    logger.info("Retrieving prompt for: %s", data_point_type)

    prompt_data = get_prompts().get(data_point_type)

    if not prompt_data:
        logger.warning("No prompt found for %s. Skipping...", data_point_type)
        return None

    return models.DataPointPrompt(prompt=prompt_data.get("prompt"), depends_on=prompt_data.get("depends_on", []))
