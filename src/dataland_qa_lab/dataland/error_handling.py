class DuplicateIDError(Exception):
    def __init__(self, data_id) -> None:
        super().__init__(f"Duplicate ID detected: {data_id}")
        self.data_id = data_id


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
        self.duplicate_ids = set()
        self.network_errors = []
        self.unknown_errors = []

    def log_duplicate_id(self, data_ids, current_data_id) -> any:
        if current_data_id in data_ids:
            self.duplicate_ids.add(current_data_id)
            raise DuplicateIDError(current_data_id)

    def log_network_error(self, error) -> any:
        self.network_errors.append(str(error))
        raise NetworkError(error)

    def log_unknown_error(self, error) -> any:
        self.unknown_errors.append(str(error))
        raise UnknownError(error)

    def report(self) -> dict[str, int]:
        report = {
            "Duplicate IDs": len(self.duplicate_ids),
            "Network Errors": len(self.network_errors),
            "Unknown Errors": len(self.unknown_errors),
        }
        return report
