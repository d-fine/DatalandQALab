from azure.ai.documentintelligence.models import AnalyzeResult

from clients.backend.dataland_backend.models.extended_data_point_nuclear_and_gas_aligned_denominator import (
    ExtendedDataPointNuclearAndGasAlignedDenominator,
)
from clients.backend.dataland_backend.models.extended_data_point_nuclear_and_gas_aligned_numerator import (
    ExtendedDataPointNuclearAndGasAlignedNumerator,
)
from clients.backend.dataland_backend.models.extended_data_point_nuclear_and_gas_eligible_but_not_aligned import (
    ExtendedDataPointNuclearAndGasEligibleButNotAligned,
)
from clients.backend.dataland_backend.models.extended_data_point_nuclear_and_gas_non_eligible import (
    ExtendedDataPointNuclearAndGasNonEligible,
)
from clients.backend.dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from clients.backend.dataland_backend.models.nuclear_and_gas_general import NuclearAndGasGeneral
from clients.backend.dataland_backend.models.nuclear_and_gas_general_general import NuclearAndGasGeneralGeneral
from clients.backend.dataland_backend.models.nuclear_and_gas_general_taxonomy_aligned_denominator import (
    NuclearAndGasGeneralTaxonomyAlignedDenominator,
)
from clients.backend.dataland_backend.models.nuclear_and_gas_general_taxonomy_aligned_numerator import (
    NuclearAndGasGeneralTaxonomyAlignedNumerator,
)
from clients.backend.dataland_backend.models.nuclear_and_gas_general_taxonomy_eligible_but_not_aligned import (
    NuclearAndGasGeneralTaxonomyEligibleButNotAligned,
)
from clients.backend.dataland_backend.models.nuclear_and_gas_general_taxonomy_non_eligible import (
    NuclearAndGasGeneralTaxonomyNonEligible,
)
from clients.qa.dataland_qa.models.qa_report_data_point_extended_data_point_yes_no import (
    QaReportDataPointExtendedDataPointYesNo,
)
from clients.qa.dataland_qa.models.qa_report_data_point_map_string_company_report import (
    QaReportDataPointMapStringCompanyReport,
)
from dataland_qa_lab.review.yes_no_value_generator import YesNoValueGenerator


class ReportGenerator:
    """Generate a quality assurance report."""

    def generate_report(self, relevant_pages: AnalyzeResult, dataset: NuclearAndGasData) -> None:
        """_summary."""
        yes_no_values = YesNoValueGenerator().extract_section_426(relevant_document=relevant_pages)

        numeric_values = None

        self.report = self.build_report_frame()

        # compare

    def build_report_frame() -> NuclearAndGasData:
        """Create Report Frame."""
        report_frame = NuclearAndGasData(
            general=NuclearAndGasGeneral(
                general=NuclearAndGasGeneralGeneral(
                    referencedReports=QaReportDataPointMapStringCompanyReport(),
                    nuclearEnergyRelatedActivitiesSection426=QaReportDataPointExtendedDataPointYesNo(),
                    nuclearEnergyRelatedActivitiesSection427=QaReportDataPointExtendedDataPointYesNo(),
                    nuclearEnergyRelatedActivitiesSection428=QaReportDataPointExtendedDataPointYesNo(),
                    fossilGasRelatedActivitiesSection429=QaReportDataPointExtendedDataPointYesNo(),
                    fossilGasRelatedActivitiesSection430=QaReportDataPointExtendedDataPointYesNo(),
                    fossilGasRelatedActivitiesSection431=QaReportDataPointExtendedDataPointYesNo(),
                ),
                taxonomyAlignedDenominator=NuclearAndGasGeneralTaxonomyAlignedDenominator(
                    nuclearAndGasTaxonomyAlignedRevenueDenominator=ExtendedDataPointNuclearAndGasAlignedDenominator(),
                    nuclearAndGasTaxonomyAlignedCapexDenominator=ExtendedDataPointNuclearAndGasAlignedDenominator(),
                ),
                taxonomyAlignedNumerator=NuclearAndGasGeneralTaxonomyAlignedNumerator(
                    nuclearAndGasTaxonomyAlignedRevenueNumerator=ExtendedDataPointNuclearAndGasAlignedNumerator(),
                    nuclearAndGasTaxonomyAlignedCapexNumerator=ExtendedDataPointNuclearAndGasAlignedNumerator(),
                ),
                taxonomyEligibleButNotAligned=NuclearAndGasGeneralTaxonomyEligibleButNotAligned(
                    nuclearAndGasTaxonomyEligibleButNotAlignedRevenue=ExtendedDataPointNuclearAndGasEligibleButNotAligned(),
                    nuclearAndGasTaxonomyEligibleButNotAlignedCapex=ExtendedDataPointNuclearAndGasEligibleButNotAligned()
                ),
                taxonomyNonEligible=NuclearAndGasGeneralTaxonomyNonEligible(
                    nuclearAndGasTaxonomyNonEligibleRevenue=ExtendedDataPointNuclearAndGasNonEligible(),
                    nuclearAndGasTaxonomyNonEligibleCapex=ExtendedDataPointNuclearAndGasNonEligible()
                )
            )
        )

        return report_frame
    
    def compare_yes_no_values() -> None:

    def compare_numeric_values() -> None:
