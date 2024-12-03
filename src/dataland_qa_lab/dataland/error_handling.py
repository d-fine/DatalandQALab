class NetworkError(Exception):
    def init(self, error) -> None:
        super().init(f"Network error occurred: {error}")
        self.error = error


class UnknownError(Exception):
    def init(self, error) -> None:
        super().init(f"Unknown error occurred: {error}")
        self.error = error


class ErrorHandling:
    def init(self) -> None:
        self.network_errors = []
        self.unknown_errors = []

    def log_network_error(self, error) -> None:
        self.network_errors.append(str(error))
        raise NetworkError(error)

    def log_unknown_error(self, error) -> None:
        self.unknown_errors.append(str(error))
        raise UnknownError(error)