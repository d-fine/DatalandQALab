import json
from pathlib import Path

from dataland_qa_lab.data_point_flow import prompts


def test_get_prompts_success(tmp_path: Path) -> None:
    """test getting prompts from JSON files in a directory."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "a.json").write_text(json.dumps({"key1": "value1"}))
    (prompts_dir / "b.json").write_text(json.dumps({"key2": "value2"}))

    result = prompts.get_prompts(prompts_dir=prompts_dir)

    assert result == {"key1": "value1", "key2": "value2"}


def test_get_prompts_empty_directory(tmp_path: Path) -> None:
    """Test getting prompts from an empty directory."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    result = prompts.get_prompts(prompts_dir=prompts_dir)
    assert result == {}
