"""Tests for the matching fixes.

Checking if the epsilon tolerance and other fixes work.
"""

from dataland_qa_lab.matching.core import improved_match_sot_and_qareport


def test_exact_match():
    """Basic test - everything matches."""
    source_of_truth = {
        "data": {
            "general": {
                "general": {
                    "field_one": {"value": "Yes"},
                    "field_two": {"value": "No"},
                }
            }
        }
    }

    qalab_report = {
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

    result = improved_match_sot_and_qareport(source_of_truth, qalab_report)

    assert result["total_fields"] == 2
    assert result["qa_accepted"] == 2
    assert result["qa_rejected"] == 0


def test_floating_point_tolerance():
    """Test the epsilon fix - 0.05 vs 0.0500001 should match."""
    source_of_truth = {
        "data": {
            "general": {
                "general": {
                    "share": {"value": 0.05},
                }
            }
        }
    }

    qalab_report = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "share": {"verdict": 0.0500001},  # slightly different
                    }
                }
            }
        }
    }

    result = improved_match_sot_and_qareport(source_of_truth, qalab_report)

    # should match with epsilon
    assert result["qa_accepted"] == 1
    assert result["qa_rejected"] == 0


def test_case_insensitive_strings():
    """YES and yes should match."""
    source_of_truth = {
        "data": {
            "general": {
                "general": {
                    "status": {"value": "YES"},
                }
            }
        }
    }

    qalab_report = {
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

    result = improved_match_sot_and_qareport(source_of_truth, qalab_report)

    assert result["qa_accepted"] == 1


def test_null_handling():
    """Check that null values don't crash."""
    source_of_truth = {
        "data": {
            "general": {
                "general": {
                    "field_with_value": {"value": "Yes"},
                    "field_null": {"value": None},
                }
            }
        }
    }

    qalab_report = {
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

    result = improved_match_sot_and_qareport(source_of_truth, qalab_report)

    # one matches, one is null so skipped
    assert result["qa_accepted"] == 1
    assert result["qa_not_attempted"] == 1


def test_mismatch_tracking():
    """Make sure mismatches get saved."""
    source_of_truth = {
        "data": {
            "general": {
                "general": {
                    "field_one": {"value": "Yes"},
                    "field_two": {"value": "No"},
                }
            }
        }
    }

    qalab_report = {
        "data": {
            "report": {
                "general": {
                    "general": {
                        "fieldOne": {"verdict": "No"},  # doesn't match
                        "fieldTwo": {"verdict": "No"},
                    }
                }
            }
        }
    }

    result = improved_match_sot_and_qareport(source_of_truth, qalab_report)

    assert result["qa_rejected"] == 1
    assert len(result["mismatches"]) == 1
    assert result["mismatches"][0]["field"] == "field_one"
