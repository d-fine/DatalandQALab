import json
from logging import getLogger
from pathlib import Path

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
