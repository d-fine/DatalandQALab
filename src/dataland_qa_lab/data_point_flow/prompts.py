import json
from logging import getLogger
from pathlib import Path

from dataland_qa_lab.data_point_flow import models
from dataland_qa_lab.utils import config

config = config.get_config()
logger = getLogger(__name__)


def get_prompts(prompts_dir: Path | None = None) -> dict:
    """Return all prompts from the prompts directory."""
    if prompts_dir is None:
        prompts_dir = Path(__file__).parent.parent / "prompts"

    if not prompts_dir.exists():
        msg = f"Prompts directory not found: {prompts_dir}"
        raise FileNotFoundError(msg)

    combined = {}
    for file in prompts_dir.glob("*.json"):
        data = json.loads(file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            logger.error("JSON file does not contain a dictionary: %s", file)
            continue
        combined.update(data)
    return combined


def get_prompt_config(data_point_type: str) -> models.DataPointPrompt | None:
    """Retrieve the validation prompt or raise an error if not found."""
    logger.info("Retrieving prompt for data point type: %s", data_point_type)
    validation_prompts = get_prompts()

    prompt = validation_prompts.get(data_point_type)
    if prompt:
        return models.DataPointPrompt(prompt=prompt.get("prompt"), depends_on=prompt.get("depends_on", []))

    logger.warning("No prompt found for data point type: %s. Skipping...", data_point_type)
    return None
