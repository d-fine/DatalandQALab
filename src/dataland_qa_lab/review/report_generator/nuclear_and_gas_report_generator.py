from dataland_qa.models import NuclearAndGasGeneral, NuclearAndGasGeneralGeneral
from dataland_qa.models.nuclear_and_gas_data import NuclearAndGasData

from dataland_qa_lab.review.report_generator import (
    denominator_report_generator,
    eligible_not_aligned_report_generator,
    non_eligible_report_generator,
    numerator_report_generator,
    yes_no_report_generator,
)
from dataland_qa_lab.review.report_generator.abstract_report_generator import ReportGenerator
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


class NuclearAndGasReportGenerator(ReportGenerator):
    """Generate a quality assurance report."""

    relevant_pages: str
    report: NuclearAndGasData

    def generate_report(self, relevant_pages: str | None, dataset: NuclearAndGasDataCollection) -> NuclearAndGasData:
        """Assemble the QA Report based on the corrected values from Azure."""
        # Initialize report and relevant pages

        self.relevant_pages = relevant_pages
        self.report = NuclearAndGasData(general=NuclearAndGasGeneral(general=NuclearAndGasGeneralGeneral()))

        self.report.general.general = yes_no_report_generator.build_yes_no_report(
            dataset=dataset, relevant_pages=relevant_pages
        )

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
        return self.report
