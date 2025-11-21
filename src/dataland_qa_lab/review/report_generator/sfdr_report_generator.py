import json
import logging

from dataland_backend.models.sfdr_data import SfdrData

from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.prompting_services.sfdr_prompting_service import SFDRPromptingService
from dataland_qa_lab.review.generate_gpt_request import GenerateGptRequest
from dataland_qa_lab.utils.sfdr_data_collection import SFDRDataCollection

from dataland_qa.models import SfdrGeneral, SfdrGeneralGeneral, SfdrEnvironmental, SfdrSocial

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
    ai_model: str | None

    def __init__(self, ai_model: str | None = None) -> None:
        """Initialize the report generator with a configurable AI model."""
        self.ai_model = ai_model

    def generate_report(self, relevant_pages: str, dataset: SFDRDataCollection) -> SfdrData:
        """Orchestrates the review process for an SFDR dataset."""

        self.relevant_pages = relevant_pages
        self.report = SfdrData(
            general=SfdrGeneral(general=SfdrGeneralGeneral())  # environmental=SfdrEnvironmental(), #social=SfdrSocial()
        )

        self.report.general.general = denominator_report_generator.build_taxonomy_aligned_denominator_report(
            dataset=dataset, relevant_pages=relevant_pages
        )

        # environmental category

        self.report.environmental.greenhouse_gas_emissions = (
            numerator_report_generator.build_taxonomy_aligned_numerator_report(
                dataset=dataset, relevant_pages=relevant_pages
            )
        )

        """
        self.report.environmental.energy_performance = (
            eligible_not_aligned_report_generator.build_taxonomy_eligible_but_not_aligned_report(
                dataset=dataset, relevant_pages=relevant_pages
            )
        )

        self.report.environmental.biodiversity = non_eligible_report_generator.build_taxonomy_non_eligible_report(
            dataset=dataset, relevant_pages=relevant_pages
        )

        self.report.environmental.water = non_eligible_report_generator.build_taxonomy_non_eligible_report(
            dataset=dataset, relevant_pages=relevant_pages
        )

        self.report.environmental.waste = non_eligible_report_generator.build_taxonomy_non_eligible_report(
            dataset=dataset, relevant_pages=relevant_pages
        )

        self.report.environmental.emissions = non_eligible_report_generator.build_taxonomy_non_eligible_report(
            dataset=dataset, relevant_pages=relevant_pages
        )

        # social category
        self.report.social.social_and_employee_matters = (
            non_eligible_report_generator.build_taxonomy_non_eligible_report(
                dataset=dataset, relevant_pages=relevant_pages
            )
        )
        self.report.social.green_security = non_eligible_report_generator.build_taxonomy_non_eligible_report(
            dataset=dataset, relevant_pages=relevant_pages
        )
        self.report.social.human_rights = non_eligible_report_generator.build_taxonomy_non_eligible_report(
            dataset=dataset, relevant_pages=relevant_pages
        )
        self.report.social.anti_corruption_and_anti_bribery = (
            non_eligible_report_generator.build_taxonomy_non_eligible_report(
                dataset=dataset, relevant_pages=relevant_pages
            )
        )

        """
        logger.info("Report generated succesfully.")

        return self.report
