import logging
from functools import cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from dataland_qa_lab.dataland.dataland_client import DatalandClient

logger = logging.getLogger(__name__)


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
        env_file=Path(__file__).parent.parent.parent.parent / ".env", env_file_encoding="utf-8"
    )

    dataland_url: str
    dataland_api_key: str

    azure_openai_api_key: str
    azure_openai_endpoint: str

    azure_docintel_api_key: str
    azure_docintel_endpoint: str

    postgres_password: str
    postgres_user: str

    pgadmin_default_email: str
    pgadmin_default_password: str

    database_connection_string: str

    @property
    def dataland_client(self) -> DatalandClient:
        """Get the Dataland client."""
        return DatalandClient(self.dataland_url, self.dataland_api_key)


@cache
def get_config() -> DatalandQaLabSettings:
    """Get the Dataland QA Lab configuration."""
    return DatalandQaLabSettings()
