"""Configuration for the matching tolerance.

The original matching was too strict and failed when values were slightly
different because of rounding errors.
"""

# tolerance for floating point comparison
DEFAULT_EPSILON = 0.01  # 1% difference is ok

# some categories need stricter tolerance
CATEGORY_EPSILON = {
    "nuclear_gas": 0.005,  # 0.5% for nuclear data
}
