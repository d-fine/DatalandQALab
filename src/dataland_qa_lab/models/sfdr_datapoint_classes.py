from dataland_backend.models.extended_data_point_big_integer import ExtendedDataPointBigInteger


class BigIntegerDatapoint:
    """Datatype for big integer datapoints."""

    datapoint: ExtendedDataPointBigInteger | None
    corrected_data: str | None
    prompt: str | None

    def __init__(self, datapoint: ExtendedDataPointBigInteger | None) -> None:
        """Initialize class with datapoint."""
        self.datapoint = datapoint
