import json
import logging

from dataland_backend.models.sfdr_data import SfdrData

from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.prompting_services.sfdr_prompting_service import SFDRPromptingService
from dataland_qa_lab.review.generate_gpt_request import GenerateGptRequest
from dataland_qa_lab.utils.sfdr_data_collection import SFDRDataCollection

logger = logging.getLogger(__name__)

# --- KONFIGURATION ---
# Hier können einfach weitere Felder hinzugefügt werden (Scope 2, 3, etc.)
# Der Key muss exakt der API-Feld-ID entsprechen!
FIELDS_TO_CHECK = {
    "scope1_ghg_emissions_in_tonnes": {
        "field_name_for_ai": "Scope 1 GHG emissions",
        "unit": "tonnes",
    },
    # BEISPIEL FÜR ZUKUNFT:
    # "scope2_ghg_emissions_location_in_t": {
    #     "field_name_for_ai": "Scope 2 GHG emissions (location-based)",
    #     "unit": "tonnes",
    # },
}


class SFDRReportGenerator:
    """Generates QA reports for SFDR datasets in a scalable way."""

    def generate_report(self, data_id: str, dataset: SfdrData) -> dict:
        """Orchestrates the review process for an SFDR dataset."""
        logger.info("Generating SFDR report for Data-ID: %s", data_id)

        # 1. Daten vorbereiten
        sfdr_collection = SFDRDataCollection(dataset)
        final_report = {}

        # 2. PDF-Seiten holen (nur einmal für alle Felder!)
        relevant_pdf = pages_provider.get_relevant_pages_of_pdf(sfdr_collection)
        if not relevant_pdf:
            logger.warning("No PDF pages found. Returning empty report.")
            return {}

        # 3. Text extrahieren (nur einmal!)
        # Wir holen alle Seitenzahlen, die für irgendeines der Felder relevant sind
        all_page_numbers = pages_provider.get_sfdr_page_numbers(sfdr_collection)

        markdown_text = text_to_doc_intelligence.get_markdown_from_dataset(
            data_id=data_id,
            relevant_pages_pdf_reader=relevant_pdf,
            page_numbers=all_page_numbers,
        )

        if not markdown_text:
            logger.warning("Could not extract markdown text.")
            return {}

        # 4. Generische Schleife über alle konfigurierten Felder
        for field_id, config in FIELDS_TO_CHECK.items():
            logger.info("--- Processing field: %s ---", field_id)

            # KI fragen
            ai_value = self._extract_ai_value(markdown_text, config)

            # Dataland-Wert holen
            dataland_value = sfdr_collection.get_value(field_id)

            # Report für dieses Feld bauen
            field_report = self._build_field_report(dataland_value, ai_value)

            final_report[field_id] = field_report

        return final_report

    @staticmethod
    def _extract_ai_value(markdown_text: str, config: dict) -> float | None:
        """Fragt die KI generisch nach einem Wert."""
        prompt = SFDRPromptingService.create_scope1_prompt(
            markdown_text
        )  # , config["field_name_for_ai"], config["unit"])
        schema = SFDRPromptingService.create_scope1_schema()

        try:
            ai_response = GenerateGptRequest.generate_gpt_request(prompt, json.dumps(schema, indent=4))

            # Antwort parsen (Dict oder Liste von Dicts)
            if isinstance(ai_response, list) and ai_response:
                ai_response = ai_response[0]

            if isinstance(ai_response, dict):
                val = ai_response.get("value")
                logger.info("AI found value: %s", val)
                return val

            logger.warning("Unexpected AI response format: %s", ai_response)

        except Exception:
            logger.exception("AI Request failed.")

        return None

    @staticmethod
    def _build_field_report(dataland_value: float | str | None, ai_value: float | None) -> dict:
        """Compares values and builds the JSON report structure."""
        # Dataland-Wert sicher in Float wandeln
        try:
            data_float = float(dataland_value) if dataland_value is not None else None
        except (ValueError, TypeError):
            data_float = None

        # AI-Wert sicher in Float wandeln (falls er als String kam)
        try:
            ai_float = float(ai_value) if ai_value is not None else None
        except (ValueError, TypeError):
            ai_float = None

        # Logik für den Verdict
        if ai_float is None:
            verdict = "QaNotAttempted"
            comment = "AI could not extract a value from the document."

        elif data_float is None:
            verdict = "QaInconclusive"
            comment = f"AI extracted {ai_float}, but Dataland has no value."

        elif ai_float == data_float:
            verdict = "QaAccepted"
            comment = "Value matches."

        else:
            verdict = "QaRejected"
            comment = f"Mismatch: AI extracted {ai_float}, Dataland has {data_float}."

        return {
            "verdict": verdict,
            "comment": comment,
            "corrected_value": ai_value if verdict == "QaRejected" else None,
        }
