from unittest.mock import MagicMock, patch

from dataland_qa_lab.utils.config import (
    DatalandQaLabSettings,
    get_config,
)


def test_settings_load_from_env(monkeypatch: MagicMock) -> None:
    """Test that settings load correctly from environment variables."""
    monkeypatch.setenv("DATALAND_URL", "https://example.com")
    monkeypatch.setenv("DATALAND_API_KEY", "secret123")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://openai-endpoint")
    monkeypatch.setenv("AZURE_DOCINTEL_API_KEY", "docintel-key")
    monkeypatch.setenv("AZURE_DOCINTEL_ENDPOINT", "https://docintel-endpoint")
    monkeypatch.setenv("DATABASE_CONNECTION_STRING", "sqlite:///tmp.db")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://slack-url")
    monkeypatch.setenv("ENVIRONMENT", "dev")
    monkeypatch.setenv("FRAMEWORKS", "sfdr, taxonomy")
    monkeypatch.setenv("SENTRY_DSN", "https://examplePublicKey@o0.ingest.sentry.io/0")
    monkeypatch.setenv("SENTRY_TRACES_SAMPLE_RATE", "0.25")

    settings = DatalandQaLabSettings()

    assert settings.dataland_url == "https://example.com"
    assert settings.dataland_api_key == "secret123"
    assert settings.azure_openai_api_key == "openai-key"
    assert settings.azure_openai_endpoint == "https://openai-endpoint"
    assert settings.azure_docintel_api_key == "docintel-key"
    assert settings.azure_docintel_endpoint == "https://docintel-endpoint"
    assert settings.database_connection_string == "sqlite:///tmp.db"
    assert settings.slack_webhook_url == "https://slack-url"
    assert settings.environment == "dev"
    assert settings.sentry_dsn == "https://examplePublicKey@o0.ingest.sentry.io/0"
    assert settings.sentry_traces_sample_rate == 0.25


def test_frameworks_list_parsing(monkeypatch: MagicMock) -> None:
    """Test that frameworks_list property parses FRAMEWORKS env variable correctly."""
    monkeypatch.setenv("DATALAND_URL", "u")
    monkeypatch.setenv("DATALAND_API_KEY", "k")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "a")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "b")
    monkeypatch.setenv("AZURE_DOCINTEL_API_KEY", "c")
    monkeypatch.setenv("AZURE_DOCINTEL_ENDPOINT", "d")
    monkeypatch.setenv("DATABASE_CONNECTION_STRING", "e")

    monkeypatch.setenv("FRAMEWORKS", " sfdr, taxonomy ,csr  ,, ")

    cfg = DatalandQaLabSettings()

    assert cfg.frameworks_list == ["sfdr", "taxonomy", "csr"]


@patch("dataland_qa_lab.utils.config.DatalandClient")
def test_dataland_client_property(mock_client_class: MagicMock, monkeypatch: MagicMock) -> None:
    """Test that dataland_client property initializes the client correctly."""
    monkeypatch.setenv("DATALAND_URL", "https://example.com")
    monkeypatch.setenv("DATALAND_API_KEY", "key123")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "a")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "b")
    monkeypatch.setenv("AZURE_DOCINTEL_API_KEY", "c")
    monkeypatch.setenv("AZURE_DOCINTEL_ENDPOINT", "d")
    monkeypatch.setenv("DATABASE_CONNECTION_STRING", "e")

    cfg = DatalandQaLabSettings()

    client = cfg.dataland_client

    mock_client_class.assert_called_once_with("https://example.com", "key123")
    assert client is mock_client_class.return_value


@patch("dataland_qa_lab.utils.config.DatalandQaLabSettings")
def test_get_config_is_cached(mock_settings_class: MagicMock) -> None:
    """Test that get_config returns a cached instance on subsequent calls."""
    instance1 = MagicMock()
    instance2 = MagicMock()

    mock_settings_class.side_effect = [instance1, instance2]

    cfg1 = get_config()

    cfg2 = get_config()

    assert cfg1 is cfg2
