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
from dataland_backend.models.extended_data_point_yes_no import ExtendedDataPointYesNo


class YesNoDatapoint:
    """Datatype for yes no datapoints."""

    datapoint: ExtendedDataPointYesNo | None
    corrected_data: str | None
    prompt: str | None

    def __init__(self, datapoint: ExtendedDataPointYesNo | None) -> None:
        """Initialize class with datapoint."""
        self.datapoint = datapoint


class TaxononmyAlignedDenominatorDatapoint:
    """Datatype for taxonomy aligned denominator datapoint."""

    datapoint: ExtendedDataPointNuclearAndGasAlignedDenominator | None
    corrected_data: str | None
    prompt: str | None

    def __init__(self, datapoint: ExtendedDataPointNuclearAndGasAlignedDenominator | None) -> None:
        """Initialize class with datapoint."""
        self.datapoint = datapoint


class TaxonomyAlignedNumeratorDatapoint:
    """Datatype for taxonomy aligned numerator datapoint."""

    datapoint: ExtendedDataPointNuclearAndGasAlignedNumerator | None
    corrected_data: str | None
    prompt: str | None

    def __init__(self, datapoint: ExtendedDataPointNuclearAndGasAlignedNumerator | None) -> None:
        """Initialize class with datapoint."""
        self.datapoint = datapoint


class TaxonomyEligibleButNotAlignedDatapoint:
    """Datatype for taxonomy eligible but not aligned datapoint."""

    datapoint: ExtendedDataPointNuclearAndGasEligibleButNotAligned | None
    corrected_data: str | None
    prompt: str | None

    def __init__(self, datapoint: ExtendedDataPointNuclearAndGasEligibleButNotAligned | None) -> None:
        """Initialize class with datapoint."""
        self.datapoint = datapoint


class TaxonomyNonEligibleDatapoint:
    """Datatype for taxonomy non eligible numerator datapoint."""

    datapoint: ExtendedDataPointNuclearAndGasNonEligible | None
    corrected_data: str | None
    prompt: str | None

    def __init__(self, datapoint: ExtendedDataPointNuclearAndGasNonEligible | None) -> None:
        """Initialize class with datapoint."""
        self.datapoint = datapoint
