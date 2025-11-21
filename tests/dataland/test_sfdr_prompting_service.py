from dataland_qa_lab.prompting_services.sfdr_prompting_service import SFDRPromptingService

def test_create_generic_numeric_prompt() -> None:
    """Test that the generic prompt is correctly structured."""
    fake_markdown = "This is a test markdown content."
    kpi_name = "Scope 1 GHG emissions"
    unit = "tonnes"

    
    prompt = SFDRPromptingService.create_generic_numeric_prompt(kpi_name, unit, fake_markdown)


    assert kpi_name in prompt
    assert unit in prompt
    assert "Return ONLY the number" in prompt
    assert fake_markdown in prompt

def test_create_generic_numeric_schema() -> None:
    """Test that the JSON schema for numeric values is correct."""
    field_id = "extracted_value"
    

    schema = SFDRPromptingService.create_generic_numeric_schema(field_id)

    assert schema
    assert field_id in schema["properties"]
    assert schema["required"] == [field_id]

    assert schema["properties"][field_id]["type"] == "number"