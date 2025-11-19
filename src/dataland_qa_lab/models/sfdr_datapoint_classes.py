from dataland_backend.models.extended_data_point_nuclear_and_gas_aligned_denominator import (
    ExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_backend.models.extended_data_point_nuclear_and_gas_aligned_numerator import (
    ExtendedDataPointNuclearAndGasAlignedNumerator,
)
from dataland_backend.models.extended_data_point_nuclear_and_gas_eligible_but_not_aligned import (
    ExtendedDataPointNuclearAndGasEligibleButNotAligned,
)
from dataland_backend.models.extended_data_point_nuclear_and_gas_non_eligible import (
    ExtendedDataPointNuclearAndGasNonEligible,
)
from dataland_backend.models.extended_data_point_big_integer import ExtendedDataPointBigInteger


class BigIntegerDatapoint:
    """Datatype for big integer datapoints."""

    datapoint: ExtendedDataPointBigInteger | None
    corrected_data: str | None
    prompt: str | None

    def __init__(self, datapoint: ExtendedDataPointBigInteger | None) -> None:
        """Initialize class with datapoint."""
        self.datapoint = datapoint
