"""Fixed version of the matching function from monitor/utils.py.

Handles:
- Float comparisons with epsilon tolerance
- Case-insensitive string matching
- Null value handling
- camel case to snake_case conversion
"""

import logging

from pydantic import BaseModel

from dataland_qa_lab.matching.config import CATEGORY_EPSILON, DEFAULT_EPSILON

logger = logging.getLogger(__name__)


class ValidationDiff(BaseModel):
    """Represents a mismatch between expected and actual values."""

    field: str
    expected: object
    actual: object


def match_dataland_and_qalab(
    dataland_data: dict,
    qalab_data: dict,
    category: str | None = None,
) -> dict:
    """Match Dataland and QALab data with epsilon tolerance.

    Args:
        dataland_data: Reference data from Dataland (expected values)
        qalab_data: Extracted data from QALab (actual values)
        category: Optional category for specific epsilon tolerance

    Returns:
        Dictionary with matching statistics and list of ValidationDiff objects
    """
    epsilon = CATEGORY_EPSILON.get(category, DEFAULT_EPSILON) if category else DEFAULT_EPSILON

    dataland_fields = extract_dataland_fields(dataland_data)
    qalab_fields = extract_qalab_fields(qalab_data)

    matches_count = 0
    mismatches_count = 0
    skipped_count = 0
    mismatches = []

    for field_name in dataland_fields:
        expected_value = dataland_fields[field_name]
        qalab_value = qalab_fields.get(field_name)

        if expected_value is None or qalab_value is None:
            skipped_count += 1
            continue

        if values_are_equal(expected_value, qalab_value, epsilon):
            matches_count += 1
        else:
            mismatches_count += 1
            mismatches.append(
                ValidationDiff(
                    field=field_name,
                    expected=expected_value,
                    actual=qalab_value,
                )
            )

    total_fields = matches_count + mismatches_count + skipped_count

    return {
        "total_fields": total_fields,
        "matches_count": matches_count,
        "mismatches_count": mismatches_count,
        "skipped_count": skipped_count,
        "mismatches": mismatches,
    }


def extract_dataland_fields(data: dict) -> dict:
    """Extract fields from Dataland data.

    Navigates the expected Dataland data structure (data.general.general) and extracts
    field values. If the data structure is malformed or missing expected keys, logs a
    warning and returns whatever fields were successfully extracted.

    Args:
        data: Dataland data dictionary with expected structure {data: {general: {general: {...}}}}

    Returns:
        Dictionary of field names to their values. Returns empty dict if:
        - Input data is not a dictionary (TypeError)
        - Required nested keys are missing or None (AttributeError when calling .get() on None)
        - Data structure doesn't match expected format
    """
    fields = {}
    try:
        general = data.get("data", {}).get("general", {}).get("general", {})
        for key, value in general.items():
            if key == "referenced_reports":
                continue

            if isinstance(value, dict) and "value" in value:
                fields[key] = value["value"]
            else:
                fields[key] = value
    except (AttributeError, TypeError) as e:
        logger.warning(
            "Failed to extract Dataland fields due to malformed data structure: %s. "
            "Data keys: %s",
            e,
            list(data.keys()) if isinstance(data, dict) else type(data).__name__,
        )

    return fields


def extract_qalab_fields(data: dict) -> dict:
    """Extract fields from QALab data.

    Navigates the expected QALab data structure (data.report.general.general) and extracts
    field values. Converts camelCase keys to snake_case for matching with Dataland fields.
    If the data structure is malformed or missing expected keys, logs a warning and
    returns whatever fields were successfully extracted.

    Args:
        data: QALab data dictionary with expected structure
              {data: {report: {general: {general: {...}}}}}

    Returns:
        Dictionary of field names (snake_case) to their values. Returns empty dict if:
        - Input data is not a dictionary (TypeError)
        - Required nested keys are missing or None (AttributeError when calling .get() on None)
        - Data structure doesn't match expected format
    """
    fields = {}
    try:
        general = data.get("data", {}).get("report", {}).get("general", {}).get("general", {})
        for key, value in general.items():
            snake_key = camel_to_snake(key)

            if isinstance(value, dict) and "verdict" in value:
                fields[snake_key] = value["verdict"]
            else:
                fields[snake_key] = value
    except (AttributeError, TypeError) as e:
        logger.warning(
            "Failed to extract QALab fields due to malformed data structure: %s. "
            "Data keys: %s",
            e,
            list(data.keys()) if isinstance(data, dict) else type(data).__name__,
        )

    return fields


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case (fieldOne -> field_one)."""
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.extend(("_", char.lower()))
        else:
            result.append(char.lower())
    return "".join(result)


def values_are_equal(value1: object, value2: object, epsilon: float) -> bool:
    """Check if two values match (uses epsilon for numbers)."""
    if value1 is None or value2 is None:
        return value1 == value2

    if isinstance(value1, str) and isinstance(value2, str):
        return value1.lower().strip() == value2.lower().strip()

    if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
        return abs(float(value1) - float(value2)) <= epsilon

    try:
        num1 = float(value1)
        num2 = float(value2)
        return abs(num1 - num2) <= epsilon
    except (ValueError, TypeError):
        pass

    return value1 == value2
