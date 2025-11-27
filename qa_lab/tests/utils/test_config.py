from qa_lab.utils.config import DatalandQaLabSettings


def test_settings_initialization() -> None:
    """Test that DatalandQaLabSettings initializes with given values."""
    settings = DatalandQaLabSettings(
        dataland_url="https://example.com",
        dataland_api_key="api-key",
        azure_openai_api_key="oaikey",
        azure_openai_endpoint="https://openai.example.com",
        azure_docintel_api_key="dockey",
        azure_docintel_endpoint="https://doc.example.com",
        database_connection_string="sqlite:///:memory:",
        slack_webhook_url="https://slack.example.com",
        environment="test",
    )

    assert settings.dataland_url == "https://example.com"
    assert settings.ai_model == "gpt-4o"
    assert settings.use_ocr is True
