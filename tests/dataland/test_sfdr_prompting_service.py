from dataland_qa_lab.prompting_services.sfdr_prompting_service import SFDRPromptingService


def test_create_generic_numeric_prompt() -> None:
    """Test that the generic prompt correctly inserts KPI, unit and text."""

    kpi_name = "Hazardous Waste Ratio"
    unit = "percent"
    fake_text = "Content of the PDF page."

    prompt = SFDRPromptingService.create_generic_numeric_prompt(kpi_name, unit, fake_text)

    assert kpi_name in prompt, "The KPI name should be in the prompt."
    assert unit in prompt, "The unit should be in the prompt."
    assert fake_text in prompt, "The source text should be in the prompt."

    assert "ESG analyst" in prompt
    assert "Return ONLY the number" in prompt
    assert "return None" in prompt


def test_create_generic_numeric_schema() -> None:
    """Test that the generic JSON schema is constructed correctly."""

    field_id = "extracted_custom_value"

    schema = SFDRPromptingService.create_generic_numeric_schema(field_id)

    assert schema["type"] == "object"

    assert field_id in schema["properties"]

    assert schema["properties"][field_id]["type"] == "number"

    assert field_id in schema["required"]


def test_create_scope1_prompt() -> None:
    """Test the legacy Scope 1 prompt."""
    fake_markdown = "This is a test markdown content."

    prompt = SFDRPromptingService.create_scope1_prompt(fake_markdown)

    assert "Scope 1 GHG emissions" in prompt
    assert "tonnes of CO2e" in prompt
    assert fake_markdown in prompt


def test_create_scope1_schema() -> None:
    """Test that the Scope 1 schema wraps the generic schema correctly."""

    schema = SFDRPromptingService.create_scope1_schema()

    assert "scope1_value" in schema["properties"]
    assert schema["properties"]["scope1_value"]["type"] == "number"
    assert schema["required"] == ["scope1_value"]
