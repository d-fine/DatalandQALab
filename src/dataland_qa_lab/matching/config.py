"""Configuration for the matching tolerance.

The original matching was too strict and failed when values were slightly
different because of rounding errors.
"""

# Default epsilon for absolute numeric comparisons.
# Unit/scale: This value represents an absolute tolerance for numeric values, typically in the range 0-100.
# Example scenario: Use DEFAULT_EPSILON for general numeric comparisons where small rounding errors may occur,
# such as comparing calculated totals or measurements.
# Guidance: If a specific category requires a tighter or looser tolerance due to domain-specific precision
# requirements, add a new entry to CATEGORY_EPSILON with an appropriate value and a comment explaining why.
DEFAULT_EPSILON = 0.01

CATEGORY_EPSILON = {
    # Nuclear/gas uses a tighter tolerance due to higher precision requirements in energy calculations.
    "nuclear_gas": 0.005,
}
