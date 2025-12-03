"""Tests for the matching fixes.

Checking if the epsilon tolerance and other fixes work.
"""

from dataland_qa_lab.matching.core import match_dataland_and_qalab


def test_exact_match() -> None:
    """Basic test - everything matches."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "field_one": {"value": "Yes"},
                    "field_two": {"value": "No"},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "fieldOne": {"verdict": "Yes"},
                        "fieldTwo": {"verdict": "No"},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    assert result["total_fields"] == 2
    assert result["matches_count"] == 2
    assert result["mismatches_count"] == 0


def test_floating_point_tolerance() -> None:
    """Test the epsilon fix - 0.05 vs 0.0500001 should match."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "share": {"value": 0.05},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "share": {"verdict": 0.0500001},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    assert result["matches_count"] == 1
    assert result["mismatches_count"] == 0


def test_case_insensitive_strings() -> None:
    """YES and yes should match."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "status": {"value": "YES"},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "status": {"verdict": "yes"},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    assert result["matches_count"] == 1


def test_null_handling() -> None:
    """Check that null values don't crash."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "field_with_value": {"value": "Yes"},
                    "field_null": {"value": None},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "fieldWithValue": {"verdict": "Yes"},
                        "fieldNull": {"verdict": "No"},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    assert result["matches_count"] == 1
    assert result["skipped_count"] == 1


def test_mismatch_tracking() -> None:
    """Make sure mismatches get saved."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "field_one": {"value": "Yes"},
                    "field_two": {"value": "No"},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "fieldOne": {"verdict": "No"},
                        "fieldTwo": {"verdict": "No"},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    assert result["mismatches_count"] == 1
    assert len(result["mismatches"]) == 1
    assert result["mismatches"][0].field == "field_one"


def test_mixed_int_float_comparison() -> None:
    """Test that 5 vs 5.0 are treated as equal."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "int_field": {"value": 5},
                    "float_field": {"value": 5.0},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "intField": {"verdict": 5.0},
                        "floatField": {"verdict": 5},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    assert result["matches_count"] == 2
    assert result["mismatches_count"] == 0


def test_boolean_values() -> None:
    """Test boolean value handling - True vs 'True' vs 'yes'."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "bool_true": {"value": True},
                    "bool_false": {"value": False},
                    "string_yes": {"value": "yes"},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "boolTrue": {"verdict": True},
                        "boolFalse": {"verdict": False},
                        "stringYes": {"verdict": "YES"},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    # Booleans should match exactly, strings case-insensitive
    assert result["matches_count"] == 3
    assert result["mismatches_count"] == 0


def test_complex_types_lists() -> None:
    """Test handling of list values."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "list_field": {"value": [1, 2, 3]},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "listField": {"verdict": [1, 2, 3]},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    # Lists should be compared with direct equality
    assert result["matches_count"] == 1
    assert result["mismatches_count"] == 0


def test_complex_types_dictionaries() -> None:
    """Test handling of dictionary values."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "dict_field": {"value": {"key": "value"}},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "dictField": {"verdict": {"key": "value"}},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    # Dictionaries should be compared with direct equality
    assert result["matches_count"] == 1
    assert result["mismatches_count"] == 0


def test_fields_in_qalab_not_in_dataland() -> None:
    """Test that fields in QALab but not in Dataland are ignored."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "field_one": {"value": "Yes"},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "fieldOne": {"verdict": "Yes"},
                        "extraField": {"verdict": "Extra"},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    # Only field_one is compared, extraField is ignored
    assert result["total_fields"] == 1
    assert result["matches_count"] == 1
    assert result["mismatches_count"] == 0


def test_empty_string_vs_none() -> None:
    """Test empty string vs None comparison."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "empty_field": {"value": ""},
                    "none_field": {"value": None},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "emptyField": {"verdict": None},
                        "noneField": {"verdict": ""},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    # None values are skipped, empty strings aren't equal to None
    assert result["skipped_count"] >= 1


def test_whitespace_only_strings() -> None:
    """Test whitespace-only strings are properly trimmed."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "whitespace_field": {"value": "  hello  "},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "whitespaceField": {"verdict": "hello"},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    # Strings should match after stripping whitespace
    assert result["matches_count"] == 1
    assert result["mismatches_count"] == 0


def test_very_large_numbers() -> None:
    """Test very large numbers."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "large_number": {"value": 1e15},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "largeNumber": {"verdict": 1e15},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    assert result["matches_count"] == 1
    assert result["mismatches_count"] == 0


def test_scientific_notation() -> None:
    """Test scientific notation comparisons."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "sci_field": {"value": 1.5e-10},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "sciField": {"verdict": 0.00000000015},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    assert result["matches_count"] == 1
    assert result["mismatches_count"] == 0


def test_numeric_string_conversion() -> None:
    """Test numeric strings are converted and compared properly."""
    dataland_data = {
        "data": {
            "general": {
                "general": {
                    "num_as_string": {"value": "42"},
                }
            }
        }
    }

    qalab_data = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "numAsString": {"verdict": 42},
                    }
                }
            }
        }
    }

    result = match_dataland_and_qalab(dataland_data, qalab_data)

    # "42" can be converted to 42.0 and should match
    assert result["matches_count"] == 1
    assert result["mismatches_count"] == 0
