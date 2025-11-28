"""Fixed version of the matching function from monitor/utils.py.

The old one was too strict and failed when:
- Numbers were slightly different (0.05 vs 0.0500001)
- Strings had different cases ("Yes" vs "yes")
- Some values were null
"""

from dataland_qa_lab.matching.config import DEFAULT_EPSILON, CATEGORY_EPSILON


def improved_match_sot_and_qareport(
    source_of_truth: dict,
    qalab_report: dict,
    category: str | None = None,
) -> dict:
    """Match Dataland and QALab data with epsilon tolerance."""
    # figure out which epsilon to use
    epsilon = CATEGORY_EPSILON.get(category, DEFAULT_EPSILON) if category else DEFAULT_EPSILON
    
    # get all the fields from both datasets
    sot_fields = extract_dataland_fields(source_of_truth)
    qa_fields = extract_qalab_fields(qalab_report)
    
    # now compare them
    qa_accepted = 0
    qa_rejected = 0
    qa_not_attempted = 0
    mismatches = []
    
    for field_name in sot_fields:
        sot_value = sot_fields[field_name]
        qa_value = qa_fields.get(field_name)
        
        # skip if either one is missing
        if sot_value is None or qa_value is None:
            qa_not_attempted += 1
            continue
        
        # see if they match
        if values_are_equal(sot_value, qa_value, epsilon):
            qa_accepted += 1
        else:
            qa_rejected += 1
            # track what didn't match
            mismatches.append({
                "field": field_name,
                "expected": sot_value,
                "actual": qa_value,
            })
    
    total_fields = qa_accepted + qa_rejected + qa_not_attempted
    
    return {
        "total_fields": total_fields,
        "qa_accepted": qa_accepted,
        "qa_rejected": qa_rejected,
        "qa_inconclusive": 0,  # not used but kept for compatibility
        "qa_not_attempted": qa_not_attempted,
        "mismatches": mismatches,
    }


def extract_dataland_fields(data: dict) -> dict:
    """Extract fields from Dataland data."""
    fields = {}
    try:
        general = data.get("data", {}).get("general", {}).get("general", {})
        for key, value in general.items():
            # don't include referenced reports
            if key in ["referencedReports", "referenced_reports"]:
                continue
            
            # extract value field
            if isinstance(value, dict) and "value" in value:
                fields[key] = value["value"]
            else:
                fields[key] = value
    except (KeyError, AttributeError, TypeError):
        pass  # just return what we got so far

    return fields


def extract_qalab_fields(data: dict) -> dict:
    """Extract fields from QALab data."""
    fields = {}
    try:
        general = data.get("data", {}).get("report", {}).get("general", {}).get("general", {})
        for key, value in general.items():
            # convert camelCase to snake_case
            snake_key = camel_to_snake(key)
            
            # qalab uses "verdict" not "value"
            if isinstance(value, dict) and "verdict" in value:
                fields[snake_key] = value["verdict"]
            else:
                fields[snake_key] = value
    except (KeyError, AttributeError, TypeError):
        pass  # just return what we got

    return fields


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case (fieldOne -> field_one)."""
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append("_")
            result.append(char.lower())
        else:
            result.append(char.lower())
    return "".join(result)


def values_are_equal(value1, value2, epsilon: float) -> bool:
    """Check if two values match (uses epsilon for numbers)."""
    # handle None values first
    if value1 is None or value2 is None:
        return value1 == value2
    
    # try comparing as numbers with epsilon tolerance
    # this fixes the 0.05 vs 0.0500001 problem
    try:
        num1 = float(value1)
        num2 = float(value2)
        return abs(num1 - num2) <= epsilon
    except (ValueError, TypeError):
        pass  # not numbers
    
    # try as strings (ignore case)
    if isinstance(value1, str) and isinstance(value2, str):
        return value1.lower().strip() == value2.lower().strip()
    
    # last resort just use ==
    return value1 == value2
