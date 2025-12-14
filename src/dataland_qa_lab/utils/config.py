import logging
from functools import cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from dataland_qa_lab.dataland.dataland_client import DatalandClient

logger = logging.getLogger(__name__)


class VisionConfig(BaseModel):
    """Configuration for Vision/Bypass OCR feature."""

    enabled: bool = False
    provider: str = "azure"
    model_name: str = "gpt-5"
    detail_level: str = "high"
    max_images_per_request: int = 10
    dpi: int = 300
    timeout: int = 200
    image_format: str = "JPEG"
    jpeg_quality: int = 85


class DatalandQaLabSettings(BaseSettings):
    """The Dataland QA Lab settings.

    Attributes:
        dataland_url (str): The URL of the Dataland instance.
        dataland_api_key (str): The API Key to use for authenticating against Dataland.
        azure_openai_api_key (str): The API Key for the Azure OpenAI service.
        azure_openai_endpoint (str): The endpoint for the Azure OpenAI service.
        azure_docintel_api_key (str): The API Key for the Azure Document Intelligence service.
        azure_docintel_endpoint (str): The endpoint for the Azure Document Intelligence service.
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
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
    frameworks: str = "sfdr"
    ai_model: str = "gpt-5"
    use_ocr: bool = True
    vision: VisionConfig = Field(default_factory=VisionConfig)

    @property
    def dataland_client(self) -> DatalandClient:
        """Get the Dataland client."""
        return DatalandClient(self.dataland_url, self.dataland_api_key)

    @property
    def frameworks_list(self) -> list[str]:
        """Get the list of frameworks."""
        return [framework.strip() for framework in self.frameworks.split(",") if framework.strip()]

    @property
    def is_dev_environment(self) -> bool:
        """Check if the environment is development."""
        return self.environment in {"dev", "development"}


@cache
def get_config() -> DatalandQaLabSettings:
    """Get the Dataland QA Lab configuration."""
    return DatalandQaLabSettings()
