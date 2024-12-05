from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_qa.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_qa.models.nuclear_and_gas_general import NuclearAndGasGeneral
from dataland_qa.models.nuclear_and_gas_general_general import NuclearAndGasGeneralGeneral
from dataland_qa.models.nuclear_and_gas_general_taxonomy_aligned_denominator import (
    NuclearAndGasGeneralTaxonomyAlignedDenominator,
)
from dataland_qa.models.nuclear_and_gas_general_taxonomy_aligned_numerator import (
    NuclearAndGasGeneralTaxonomyAlignedNumerator,
)
from dataland_qa.models.nuclear_and_gas_general_taxonomy_eligible_but_not_aligned import (
    NuclearAndGasGeneralTaxonomyEligibleButNotAligned,
)
from dataland_qa.models.nuclear_and_gas_general_taxonomy_non_eligible import (
    NuclearAndGasGeneralTaxonomyNonEligible,
)
from dataland_qa.models.qa_report_data_point_extended_data_point_yes_no import (
    QaReportDataPointExtendedDataPointYesNo,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.review.yes_no_value_generator import YesNoValueGenerator


class ReportGenerator:
    """Generate a quality assurance report."""

    def generate_report(self, relevant_pages: AnalyzeResult, dataset: NuclearAndGasData) -> None:
        """_summary."""
        self.relevant_pages = relevant_pages

        self.report = self.build_report_frame()

        return self.report

        # compare

    @classmethod
    def build_report_frame(cls) -> NuclearAndGasData:
        """Create Report Frame."""
        report_frame = NuclearAndGasData(
            general=NuclearAndGasGeneral(
                general=NuclearAndGasGeneralGeneral(),
                taxonomyAlignedDenominator=NuclearAndGasGeneralTaxonomyAlignedDenominator(),
                taxonomyAlignedNumerator=NuclearAndGasGeneralTaxonomyAlignedNumerator(),
                taxonomyEligibleButNotAligned=NuclearAndGasGeneralTaxonomyEligibleButNotAligned(),
                taxonomyNonEligible=NuclearAndGasGeneralTaxonomyNonEligible()
            )
        )

        return report_frame

    def compare_yes_no_values(self) -> None:
        """Build first yes no data point."""
        yes_no_values = YesNoValueGenerator().extract_section_426(relevant_document=self.relevant_pages)

        qa_data_points = []
        qa_data_points.extend(QaReportDataPointExtendedDataPointYesNo(
            comment="QA",
            verdict=QaReportDataPointVerdict.QAACCEPTED,
            correctedData=ExtendedDataPointYesNo(value=yes_no_values)))

        self.report.general.general.nuclear_energy_related_activities_section426 = qa_data_points[0]
