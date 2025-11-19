import json
import logging

from dataland_backend.models.sfdr_data import SfdrData

from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.prompting_services.sfdr_prompting_service import SFDRPromptingService
from dataland_qa_lab.review.generate_gpt_request import GenerateGptRequest
from dataland_qa_lab.utils.sfdr_data_collection import SFDRDataCollection

from dataland_qa.models import SfdrGeneral, SfdrGeneralGeneral

from dataland_qa_lab.review.report_generator import (
    denominator_report_generator,
    eligible_not_aligned_report_generator,
    non_eligible_report_generator,
    numerator_report_generator,
    yes_no_report_generator,
)

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


class SfdrReportGenerator:
    """Generates QA reports for SFDR datasets in a scalable way."""

    relevant_pages: str
    report: SfdrData

    def generate_report(self, relevant_pages: str, dataset: SFDRDataCollection) -> SfdrData:
        """Orchestrates the review process for an SFDR dataset."""

        self.relevant_pages = relevant_pages
        self.report = SfdrData(general=SfdrGeneral(general=SfdrGeneralGeneral()))

        self.report.general.taxonomy_aligned_denominator = (
            denominator_report_generator.build_taxonomy_aligned_denominator_report(
                dataset=dataset, relevant_pages=relevant_pages
            )
        )

        self.report.general.taxonomy_aligned_numerator = (
            numerator_report_generator.build_taxonomy_aligned_numerator_report(
                dataset=dataset, relevant_pages=relevant_pages
            )
        )

        self.report.general.taxonomy_eligible_but_not_aligned = (
            eligible_not_aligned_report_generator.build_taxonomy_eligible_but_not_aligned_report(
                dataset=dataset, relevant_pages=relevant_pages
            )
        )

        self.report.general.taxonomy_non_eligible = non_eligible_report_generator.build_taxonomy_non_eligible_report(
            dataset=dataset, relevant_pages=relevant_pages
        )

        logger.info("Report generated succesfully.")

        return self.report
