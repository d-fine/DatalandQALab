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

from dataland_qa_lab.dataland.data_provider import DataProvider
from dataland_qa_lab.review.yes_no_value_generator import YesNoValueGenerator


class ReportGenerator:
    """Generate a quality assurance report."""

    def generate_report(self, relevant_pages: AnalyzeResult, dataset: NuclearAndGasData) -> None:
        """_summary."""
        self.relevant_pages = relevant_pages
        self.dataset = dataset

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
                taxonomyNonEligible=NuclearAndGasGeneralTaxonomyNonEligible(),
            )
        )

        return report_frame

    def compare_yes_no_values(self) -> None:
        """Build first yes no data point."""
        yes_no_values = YesNoValueGenerator().extract_section_426(relevant_document=self.relevant_pages)
        yes_no_values_from_dataland = DataProvider().get_values_by_data(data=self.dataset)
        data_sources = DataProvider().get_datasources_of_data_points(data=self.dataset)

        qa_data_points = []

        for i in range(5):
            corrected_value = yes_no_values[i]
            dataland_value = yes_no_values_from_dataland[i]

            if corrected_value != dataland_value:
                qa_data_points[i] = QaReportDataPointExtendedDataPointYesNo(
                    comment="tbd",
                    verdict=QaReportDataPointVerdict.QAACCEPTED,
                    correctedData=ExtendedDataPointYesNo(
                        value=corrected_value, quality="?", comment="justification", dataSource=data_sources[i]
                    ),
                )
            else:
                qa_data_points[i] = QaReportDataPointExtendedDataPointYesNo(
                    comment="tbd", verdict=QaReportDataPointVerdict.QAREJECTED
                )

        self.report.general.general.nuclear_energy_related_activities_section426 = qa_data_points[0]
        self.report.general.general.nuclear_energy_related_activities_section427 = qa_data_points[1]
        self.report.general.general.nuclear_energy_related_activities_section428 = qa_data_points[2]
        self.report.general.general.fossil_gas_related_activities_section429 = qa_data_points[3]
        self.report.general.general.fossil_gas_related_activities_section430 = qa_data_points[4]
        self.report.general.general.fossil_gas_related_activities_section431 = qa_data_points[5]
