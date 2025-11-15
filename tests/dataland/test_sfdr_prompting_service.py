from dataland_qa_lab.prompting_services.sfdr_prompting_service import SFDRPromptingService


def test_create_scope1_prompt() -> None:
    """Test that the prompt contains key instructions and the input text."""
    fake_markdown = "This is a test markdown content."

    prompt = SFDRPromptingService.create_scope1_prompt(fake_markdown)

    assert "Scope 1 GHG emissions" in prompt
    assert "tonnes" in prompt
    assert "Ignore Scope 2" in prompt
    assert fake_markdown in prompt


def test_create_scope1_schema() -> None:
    """Test that the JSON schema is correctly structured."""

    schema = SFDRPromptingService.create_scope1_schema()

    assert schema
    assert "scope1_value" in schema["properties"]
    assert schema["required"] == ["scope1_value"]
    assert schema["properties"]["scope1_value"]["type"] == "number"
