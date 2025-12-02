"""Configuration for the matching tolerance.

The original matching was too strict and failed when values were slightly
different because of rounding errors.
"""

DEFAULT_EPSILON = 0.01

CATEGORY_EPSILON = {
    "nuclear_gas": 0.005,
}
