class DuplicateIDError(Exception):
    """Exception für doppelte IDs."""
    def __init__(self, data_id) -> None:
        super().__init__(f"Duplicate ID detected: {data_id}")
        self.data_id = data_id


class NetworkError(Exception):
    """Exception für Netzwerkfehler."""
    def __init__(self, error) -> None:
        super().__init__(f"Network error occurred: {error}")
        self.error = error


class UnknownError(Exception):
    """Exception für unbekannte Fehler."""
    def __init__(self, error) -> None:
        super().__init__(f"Unknown error occurred: {error}")
        self.error = error


class ErrorHandling:
    def __init__(self) -> None:
        self.duplicate_ids = set()  # Set für doppelte IDs
        self.network_errors = []  # Liste für Netzwerkfehler
        self.unknown_errors = []  # Liste für unbekannte Fehler

    def log_duplicate_id(self, data_ids, current_data_id) -> any:
        """Loggt eine doppelte ID."""
        if current_data_id in data_ids:
            self.duplicate_ids.add(current_data_id)
            raise DuplicateIDError(current_data_id)

    def log_network_error(self, error) -> any:
        """Loggt einen Netzwerkfehler."""
        self.network_errors.append(str(error))
        raise NetworkError(error)

    def log_unknown_error(self, error) -> any:
        """Loggt einen unbekannten Fehler."""
        self.unknown_errors.append(str(error))
        raise UnknownError(error)

    def report(self) -> dict[str, int]:
        """Erstellt einen Bericht über alle Fehler."""
        report = {
            "Duplicate IDs": len(self.duplicate_ids),
            "Network Errors": len(self.network_errors),
            "Unknown Errors": len(self.unknown_errors),
        }
        return report
