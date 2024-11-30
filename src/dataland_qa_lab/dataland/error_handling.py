class NetworkError(Exception):
    def __init__(self, error) -> None:
        super().__init__(f"Network error occurred: {error}")
        self.error = error


class UnknownError(Exception):
    def __init__(self, error) -> None:
        super().__init__(f"Unknown error occurred: {error}")
        self.error = error


class ErrorHandling:
    def __init__(self) -> None:
        self.network_errors = []
        self.unknown_errors = []

    def log_network_error(self, error) -> None:
        self.network_errors.append(str(error))
        raise NetworkError(error)

    def log_unknown_error(self, error) -> None:
        self.unknown_errors.append(str(error))
        raise UnknownError(error)

    def report(self) -> dict[str, int]:
        return {
            "Network Errors": len(self.network_errors),
            "Unknown Errors": len(self.unknown_errors),
        }
