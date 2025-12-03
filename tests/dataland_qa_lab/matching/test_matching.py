"""Tests for the matching fixes.

Checking if the epsilon tolerance and other fixes work.
"""

import pytest

from dataland_qa_lab.matching.core import camel_to_snake, match_dataland_and_qalab


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


class TestCamelToSnake:
    """Tests for the camel_to_snake function."""

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("fieldOne", "field_one"),
            ("fieldTwo", "field_two"),
            ("simpleCase", "simple_case"),
            ("camelCaseTest", "camel_case_test"),
        ],
    )
    def test_basic_camel_case(self, input_val: str, expected: str) -> None:
        """Test basic camelCase to snake_case conversion."""
        assert camel_to_snake(input_val) == expected

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("XMLParser", "xml_parser"),
            ("HTTPSConnection", "https_connection"),
            ("getHTTPResponse", "get_http_response"),
            ("IOError", "io_error"),
        ],
    )
    def test_acronyms(self, input_val: str, expected: str) -> None:
        """Test that consecutive uppercase letters (acronyms) are handled correctly."""
        assert camel_to_snake(input_val) == expected

    @pytest.mark.parametrize(
        "input_val,expected",
        [
            ("a", "a"),
            ("A", "a"),
            ("ABC", "abc"),
            ("lowercase", "lowercase"),
        ],
    )
    def test_edge_cases(self, input_val: str, expected: str) -> None:
        """Test edge cases like single characters and all-uppercase."""
        assert camel_to_snake(input_val) == expected
