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
    ai_model: str = "gpt-4o"

    def __init__(self, ai_model: str = "gpt-4o") -> None:
        """Initialize the report generator with a configurable AI model."""
        self.ai_model = ai_model

    def generate_report(self, relevant_pages: str, dataset: SFDRDataCollection) -> SfdrData:
        """Orchestrates the review process for an SFDR dataset."""
        self.relevant_pages = relevant_pages

        self.report = SfdrData(
            environmental=SfdrEnvironmental(
                greenhouse_gas_emissions=SfdrEnvironmentalGreenhouseGasEmissions(),
                water=SfdrEnvironmentalWater(),
                waste=SfdrEnvironmentalWaste(),
            ),
            social=SfdrSocial(social_and_employee_matters=SfdrSocialSocialAndEmployeeMatters()),
        )

        logger.info("Starting SFDR Review...")

        # --- ENVIRONMENTAL ---

        # 1. Scope 1 GHG
        logger.info("Reviewing Scope 1 GHG...")
        self.report.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes = self._review_numeric_field(
            dataset=dataset,
            relevant_pages=relevant_pages,
            kpi_name_ai="Scope 1 GHG emissions",
            unit_ai="tonnes CO2e",
            category="environmental",
            subcategory="greenhouse_gas_emissions",
            field_name="scope1_ghg_emissions_in_tonnes",
        )

        # 2. Water (Emissions to Water)
        logger.info("Reviewing Water Emissions...")
        self.report.environmental.water.emissions_to_water_in_tonnes = self._review_numeric_field(
            dataset=dataset,
            relevant_pages=relevant_pages,
            kpi_name_ai="Emissions to water",
            unit_ai="tonnes",
            category="environmental",
            subcategory="water",
            field_name="emissions_to_water_in_tonnes",
        )

        # 3. Waste (Hazardous Waste Ratio)
        logger.info("Reviewing Hazardous Waste...")
        self.report.environmental.waste.hazardous_and_radioactive_waste_in_tonnes = self._review_numeric_field(
            dataset=dataset,
            relevant_pages=relevant_pages,
            kpi_name_ai="Share of hazardous waste",
            unit_ai="percent",
            category="environmental",
            subcategory="waste",
            field_name="hazardous_and_radioactive_waste_in_tonnes",
        )

        # --- SOCIAL ---

        # 4. Gender Pay Gap
        logger.info("Reviewing Gender Pay Gap...")
        self.report.social.social_and_employee_matters.board_gender_diversity_supervisory_board_in_percent = (
            self._review_numeric_field(
                dataset=dataset,
                relevant_pages=relevant_pages,
                kpi_name_ai="Unadjusted gender pay gap",
                unit_ai="percent",
                category="social",
                subcategory="social_and_employee_matters",
                field_name="board_gender_diversity_supervisory_board_in_percent",
            )
        )

        logger.info("SFDR Report generated succesfully.")
        return self.report

    def _review_numeric_field(
        self,
        dataset: SFDRDataCollection,
        relevant_pages: str,
        kpi_name_ai: str,
        unit_ai: str,
        category: str,
        subcategory: str,
        field_name: str,
    ) -> QaReportDataPointExtendedDataPointBigDecimal:
        """Review logic for a single numeric field."""
        if not relevant_pages:
            return self._create_not_attempted("No relevant pages found")

        ai_value = SFDRNumericValueGenerator.get_generic_numeric_value(
            relevant_pages, kpi_name_ai, unit_ai, ai_model=self.ai_model
        )

        dataland_value = dataset.get_value_generic(category, subcategory, field_name)

        return self._compare_values(dataland_value, ai_value)

    def _compare_values(
        self, dataland_val: float | None, ai_val: float | None
    ) -> QaReportDataPointExtendedDataPointBigDecimal:
        """Compare logic handling None values correctly."""
        if dataland_val is None:
            if ai_val is not None:
                return self._create_entry(
                    self, QaReportDataPointVerdict.QAREJECTED, f"Dataland empty, AI found {ai_val}", ai_val
                )
            return self._create_entry(self, QaReportDataPointVerdict.QAACCEPTED, "Both empty")

        if ai_val is None:
            return self._create_entry(
                self,
                QaReportDataPointVerdict.QAREJECTED,
                f"Value in Dataland ({dataland_val}) but AI found nothing.",
                quality="NoDataFound",
            )

        try:
            dl_float = float(dataland_val)

            diff = abs(dl_float - ai_val)
            if diff <= 0.1:
                return self._create_entry(QaReportDataPointVerdict.QAACCEPTED, "Values match")
            return self._create_entry(
                QaReportDataPointVerdict.QAREJECTED,
                f"Discrepancy: Dataland {dl_float} vs AI {ai_val}",
                ai_val,
            )
        except Exception:
            return self._create_not_attempted("Comparison Error (Type mismatch)")

    @staticmethod
    def _create_entry(
        self, verdict: QaReportDataPointVerdict, comment: str, corrected_val: float = None, quality: str = "Reported"
    ) -> QaReportDataPointExtendedDataPointBigDecimal:
        """Creates the return object."""
        data = ExtendedDataPointBigDecimal()
        if verdict == QaReportDataPointVerdict.QAREJECTED and corrected_val is not None:
            data.value = corrected_val
            data.quality = quality

        return QaReportDataPointExtendedDataPointBigDecimal(comment=comment, verdict=verdict, correctedData=data)

    def _create_not_attempted(self, msg: str) -> QaReportDataPointExtendedDataPointBigDecimal:
        """Creates a not-attempted entry."""
        return QaReportDataPointExtendedDataPointBigDecimal(
            comment=msg, verdict=QaReportDataPointVerdict.QANOTATTEMPTED, correctedData=ExtendedDataPointBigDecimal()
        )
