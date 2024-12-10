class NetworkError(Exception):
    """Log network errors."""

    def __init__(self, error: any) -> None:
        """Constructor."""
        super().__init__(f"Network error occurred: {error}")
        self.error = error


class UnknownError(Exception):
    """log unkwnown errors."""

    def __init__(self, error: any) -> None:
        """Constructor."""
        super().__init__(f"Unknown error occurred: {error}")
        self.error = error
