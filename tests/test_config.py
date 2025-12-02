import os

import pytest

from dataland_qa_lab.utils.config import DatalandQaLabSettings, get_config


def test_model_validation_valid() -> None:
    """Test that valid model names work."""
    os.environ["AI_MODEL_NAME"] = "gpt-4o"
    settings = DatalandQaLabSettings()
    assert settings.ai_model_name == "gpt-4o"


def test_model_validation_invalid() -> None:
    """Test that invalid model names raise error."""
    os.environ["AI_MODEL_NAME"] = "invalid-model"
    with pytest.raises(ValueError, match="Invalid AI model name"):
        DatalandQaLabSettings()


def test_model_validation_gpt5() -> None:
    """Test that gpt-5 is accepted."""
    os.environ["AI_MODEL_NAME"] = "gpt-5"
    settings = DatalandQaLabSettings()
    assert settings.ai_model_name == "gpt-5"


def test_default_model_when_no_env_var() -> None:
    """Test that default model is used when no environment variable is set."""
    if "AI_MODEL_NAME" in os.environ:
        del os.environ["AI_MODEL_NAME"]
    settings = DatalandQaLabSettings()
    assert settings.ai_model_name == "gpt-4o"


def test_model_name_in_error_message() -> None:
    """Test that error message includes the invalid model name."""
    os.environ["AI_MODEL_NAME"] = "invalid-model"
    with pytest.raises(ValueError, match="Invalid AI model name") as exc_info:
        DatalandQaLabSettings()
    assert "invalid-model" in str(exc_info.value)
    assert "gpt-4o" in str(exc_info.value)
    assert "gpt-5" in str(exc_info.value)


def test_multiple_validation_scenarios() -> None:
    """Test multiple valid and invalid scenarios."""
    test_cases = [
        ("gpt-4o", True),
        ("gpt-5", True),
        ("GPT-4O", False),
        ("gpt4", False),
        ("", False),
    ]

    for model_name, should_pass in test_cases:
        os.environ["AI_MODEL_NAME"] = model_name
        if should_pass:
            settings = DatalandQaLabSettings()
            assert settings.ai_model_name == model_name
        else:
            with pytest.raises(ValueError, match="Invalid AI model name"):
                DatalandQaLabSettings()


def test_config_caching() -> None:
    """Test that get_config uses caching."""
    os.environ["AI_MODEL_NAME"] = "gpt-4o"

    config1 = get_config()
    config2 = get_config()

    assert config1 is config2
    assert config1.ai_model_name == config2.ai_model_name
    assert config1.ai_model_name == "gpt-4o"
