import json
from pathlib import Path

import requests

from dataland_qa_lab.utils.config import get_config
from dataland_qa_lab.validator.dataland import get_data_point, get_document

conf = get_config()

prompts = json.loads(Path("src/dataland_qa_lab/validator/prompts.json").read_text(encoding="utf-8"))


def validate_datapoint(data_point_id: str, document_id: str, relevant_pages: list[int]) -> dict | None:
    """Validate a datapoint using predefined prompts."""
    # todo: use the openai thing instead
    data_point = get_data_point(data_point_id)
    data_point_type = data_point.get("dataPointType")
    print(data_point_type)
    # document = get_document(document_id)

    print(data_point)


validate_datapoint("1bc6f8b1-d1c3-4388-926f-ca909ef84379", "test_doc", [1, 2, 3])
