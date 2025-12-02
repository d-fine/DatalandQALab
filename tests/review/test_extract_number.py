import pytest

from dataland_qa_lab.review.numeric_value_generator import NumericValueGenerator

NumericInput = str | int | float


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("12", 12.0),
        (" 12 ", 12.0),
        ("3.14", 3.14),  # noqa: FURB152
        ("  3.14  ", 3.14),  # noqa: FURB152
        ("abc 12 def", 12.0),
        ("abc -12 def", -12.0),
        ("12.5 kg", 12.5),
        ("Temp: -2°C", -2.0),
        (0, 0.0),
        (5, 5.0),
        (3.5, 3.5),
        ("-0.5", -0.5),
        ("0.5", 0.5),
        ("\u221210", -10.0),
        ("\u201310", -10.0),
    ],
)
def test_extract_number_valid_cases(value: NumericInput, expected: float) -> None:
    assert NumericValueGenerator.extract_number(value) == pytest.approx(expected)


@pytest.mark.parametrize(
    "value",
    [
        -1,
        -1.0,
        "-1",
        " -1 ",
        "\u22121",
        "\u20131",
    ],
)
def test_extract_number_reject_minus_one(value: NumericInput) -> None:
    assert NumericValueGenerator.extract_number(value) is None


@pytest.mark.parametrize(
    "value",
    [
        "",
        "abc",
        "kein wert",
        "++--",
    ],
)
def test_extract_number_raises_value_error_when_no_number(value: str) -> None:
    with pytest.raises(ValueError, match="Could not extract a valid number"):
        NumericValueGenerator.extract_number(value)
