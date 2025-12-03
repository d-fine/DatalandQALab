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
    assert result["mismatches_count"] == 0
    assert result["skipped_count"] == 0


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
