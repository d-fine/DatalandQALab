from dataland_qa_lab.dataland.error_handling import ErrorHandling, DuplicateIDError, NetworkError, UnknownError
from dataland_qa_lab.dataland.unreviewed_datasets import UnreviewedDatasets


class ScheduleProcessing:
    def __init__(self):
        self.error_handler = ErrorHandling()  # Instanz für Fehlerbehandlung
        self.unreviewed_datasets = UnreviewedDatasets()  # Instanz der UnreviewedDatasets-Klasse


    def automated_script(self):
        """Führt die Verarbeitung in einer Schleife aus."""
        while not self.unreviewed_datasets.is_empty():
            try:
                # Älteste `data_id` abrufen
                current_data_id = self.unreviewed_datasets.get_oldest_dataid()
                if not current_data_id:
                    print("No more data IDs to process.")
                    break

                # Doppelte IDs prüfen und verarbeiten
                self.error_handler.log_duplicate_id(
                    self.unreviewed_datasets.data_ids
                )

            except DuplicateIDError as e:
                # Fehlerprotokollierung für doppelte IDs
                print(f"DuplicateIDError handled: {e}")

            except NetworkError as e:
                # Fehlerprotokollierung für Netzwerkprobleme
                print(f"NetworkError handled: {e}")

            except Exception as e:
                # Protokollierung unbekannter Fehler
                self.error_handler.log_unknown_error(e)
                print(f"UnknownError handled: {e}")

            # Liste der Daten aktualisieren
            self.unreviewed_datasets.update_datasets()

        # Abschließender Bericht über Fehler
        print("Processing complete. Error report:")
        print(self.error_handler.report())
