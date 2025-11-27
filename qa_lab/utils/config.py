import logging
from functools import cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class DatalandQaLabSettings(BaseSettings):
    """The Dataland QA Lab settings."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    dataland_url: str
    dataland_api_key: str

    azure_openai_api_key: str
    azure_openai_endpoint: str

    azure_docintel_api_key: str
    azure_docintel_endpoint: str

    database_connection_string: str

    slack_webhook_url: str | None = None
    environment: str | None = None

    ai_model: str = "gpt-4o"
    use_ocr: bool = True


@cache
def get_config() -> DatalandQaLabSettings:
    """Get the Dataland QA Lab configuration."""
    return DatalandQaLabSettings()
