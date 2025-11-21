import os

import pytest

from dataland_qa_lab.utils.config import DatalandQaLabSettings


def test_model_validation_valid() -> None:
    """Test that valid model names work"""
    # Cache umgehen - direkt die Settings Klasse testen
    os.environ["AI_MODEL_NAME"] = "gpt-4o"
    settings = DatalandQaLabSettings()
    assert settings.ai_model_name == "gpt-4o"


def test_model_validation_invalid() -> None:
    """Test that invalid model names raise error"""
    os.environ["AI_MODEL_NAME"] = "invalid-model"
    with pytest.raises(ValueError, match="Invalid AI model name"):
        DatalandQaLabSettings()


def test_model_validation_gpt5() -> None:
    """Test that gpt-5 is accepted"""
    os.environ["AI_MODEL_NAME"] = "gpt-5"
    settings = DatalandQaLabSettings()
    assert settings.ai_model_name == "gpt-5"


# Add these tests to your test_config.py


def test_default_model_when_no_env_var():
    """Test that default model is used when no environment variable is set"""
    if "AI_MODEL_NAME" in os.environ:
        del os.environ["AI_MODEL_NAME"]
    settings = DatalandQaLabSettings()
    assert settings.ai_model_name == "gpt-4o"


def test_model_name_in_error_message():
    """Test that error message includes the invalid model name"""
    os.environ["AI_MODEL_NAME"] = "invalid-model"
    try:
        DatalandQaLabSettings()
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "invalid-model" in str(e)
        assert "gpt-4o" in str(e)
        assert "gpt-5" in str(e)


def test_multiple_validation_scenarios():
    """Test multiple valid and invalid scenarios"""
    test_cases = [
        ("gpt-4o", True),
        ("gpt-5", True),
        ("GPT-4O", False),  # case sensitive
        ("gpt4", False),
        ("", False),
    ]

    for model_name, should_pass in test_cases:
        os.environ["AI_MODEL_NAME"] = model_name
        if should_pass:
            settings = DatalandQaLabSettings()
            assert settings.ai_model_name == model_name
        else:
            with pytest.raises(ValueError):
                DatalandQaLabSettings()


def test_config_caching():
    """Test that get_config uses caching."""
    import os
    from dataland_qa_lab.utils.config import get_config

    # Set a specific model for this test
    os.environ["AI_MODEL_NAME"] = "gpt-4o"

    # First call
    config1 = get_config()
    # Second call should return cached instance
    config2 = get_config()

    # Should be the same object (cached)
    assert config1 is config2
    assert config1.ai_model_name == config2.ai_model_name
    assert config1.ai_model_name == "gpt-4o"
