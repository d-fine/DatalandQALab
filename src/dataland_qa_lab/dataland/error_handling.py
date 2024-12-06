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


class ErrorHandling:
    """Error handling class."""

    def __init__(self) -> None:
        """Constructor."""
        self.network_errors = []
        self.unknown_errors = []

    def log_network_error(self, error: any) -> None:
        """Network error."""
        self.network_errors.append(str(error))
        raise NetworkError(error)

    def log_unknown_error(self, error: any) -> None:
        """Unknown error."""
        self.unknown_errors.append(str(error))
        raise UnknownError(error)
