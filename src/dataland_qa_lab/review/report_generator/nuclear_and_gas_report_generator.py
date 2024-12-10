from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData as NuclearAndGasDataBackend
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

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review import yes_no_value_generator
from dataland_qa_lab.review.report_generator.abstract_report_generator import ReportGenerator


class NuclearAndGasReportGenerator(ReportGenerator):
    """Generate a quality assurance report."""

    relevant_pages: AnalyzeResult
    report: NuclearAndGasData

    def generate_report(self, relevant_pages: AnalyzeResult, dataset: NuclearAndGasDataBackend) -> NuclearAndGasData:
        """Assemble the QA Report based on the corrected values from Azure."""
        self.relevant_pages = relevant_pages

        self.report = self.build_report_frame()

        yes_no_data_points = self.compare_yes_no_values(dataset=dataset, relevant_pages=relevant_pages)

        self.report.general.general.nuclear_energy_related_activities_section426 = yes_no_data_points[0]
        self.report.general.general.nuclear_energy_related_activities_section427 = yes_no_data_points[1]
        self.report.general.general.nuclear_energy_related_activities_section428 = yes_no_data_points[2]
        self.report.general.general.fossil_gas_related_activities_section429 = yes_no_data_points[3]
        self.report.general.general.fossil_gas_related_activities_section430 = yes_no_data_points[4]
        self.report.general.general.fossil_gas_related_activities_section431 = yes_no_data_points[5]

        return self.report

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

    @classmethod
    def compare_yes_no_values(
        cls, dataset: NuclearAndGasDataBackend, relevant_pages: AnalyzeResult
    ) -> dict[str, QaReportDataPointExtendedDataPointYesNo | None]:
        """Build first yes no data point."""
        yes_no_values = yes_no_value_generator.extract_yes_no_template(relevant_document=relevant_pages)
        yes_no_values_from_dataland = data_provider.get_yes_no_values_by_data(data=dataset)
        data_sources = data_provider.get_datasources_of_nuclear_and_gas_yes_no_questions(data=dataset)

        qa_data_points = {}

        for key, dataland_value in yes_no_values_from_dataland.items():
            corrected_value = yes_no_values.get(key)
            data_source = data_sources.get(key)

            if corrected_value != dataland_value:
                qa_data_points[key] = QaReportDataPointExtendedDataPointYesNo(
                    comment="tbd",
                    verdict=QaReportDataPointVerdict.QAREJECTED,
                    correctedData=ExtendedDataPointYesNo(
                        value=corrected_value,
                        quality="Incomplete",
                        comment="justification",
                        dataSource=data_source,
                    ),
                )
            else:
                qa_data_points[key] = QaReportDataPointExtendedDataPointYesNo(
                    comment="Geprüft durch AzureOpenAI",
                    verdict=QaReportDataPointVerdict.QAACCEPTED,
                    correctedData=ExtendedDataPointYesNo(),
                )

        return qa_data_points
