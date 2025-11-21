import logging

try:
    from dataland_qa.models.sfdr_data import SfdrData
except ImportError:
    from dataland_qa.models import SfdrData


from dataland_qa.models import (
    ExtendedDataPointBigDecimal,
    QaReportDataPointExtendedDataPointBigDecimal,
    QaReportDataPointVerdict,
    SfdrEnvironmental,
    SfdrEnvironmentalGreenhouseGasEmissions,
    SfdrEnvironmentalWaste,
    SfdrEnvironmentalWater,
    SfdrSocial,
    SfdrSocialSocialAndEmployeeMatters,
)

from dataland_qa_lab.review.report_generator.sfdr_numeric_value_generator import SFDRNumericValueGenerator
from dataland_qa_lab.utils.sfdr_data_collection import SFDRDataCollection

logger = logging.getLogger(__name__)


class SfdrReportGenerator:
    """Generates QA reports for SFDR datasets covering Environmental and Social topics."""

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
            #            general=SfdrGeneral(general=SfdrGeneralGeneral()), environmental=SfdrEnvironmental(), #social=SfdrSocial()
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
