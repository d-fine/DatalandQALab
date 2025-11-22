import pytest
from unittest.mock import MagicMock, patch, ANY

from dataland_qa.models import QaReportDataPointVerdict
from dataland_qa_lab.review.report_generator.sfdr_report_generator import SfdrReportGenerator

class TestSfdrReportGenerator:
    """
    Tests for the SfdrReportGenerator class.
    We mock the 'SFDRNumericValueGenerator' (AI) and 'SFDRDataCollection' (Database/Dataland)
    to test the comparison logic and report structure purely.
    """

    @pytest.fixture
    def mock_dataset(self) -> MagicMock:
        """Mocks the dataset wrapper to control returned values from Dataland."""
        return MagicMock()

    @patch("dataland_qa_lab.review.report_generator.sfdr_report_generator.SFDRNumericValueGenerator")
    def test_generate_report_mixed_scenarios(
        self, mock_numeric_generator: MagicMock, mock_dataset: MagicMock
    ) -> None:
        """
        Test a full run where different KPIs have different outcomes:
        1. Scope 1: Match -> ACCEPTED
        2. Water: Discrepancy -> REJECTED (Corrected by AI)
        3. Waste: Dataland Empty -> REJECTED (Filled by AI)
        4. Social: AI Empty -> REJECTED (NoDataFound)
        """
        
        # 1. Setup Generator
        generator = SfdrReportGenerator(ai_model="gpt-4o")
        relevant_pages = "Dummy content page 1-5"

        # 2. Mock AI Responses (SFDRNumericValueGenerator.get_generic_numeric_value)
        # We use side_effect to return different values based on the KPI name requested
        def ai_side_effect(pages, kpi_name, unit, ai_model):
            if "Scope 1" in kpi_name:
                return 100.0
            if "Emissions to water" in kpi_name:
                return 50.0
            if "hazardous waste" in kpi_name:
                return 10.0
            if "gender pay gap" in kpi_name:
                return None  # AI finds nothing
            return None

        mock_numeric_generator.get_generic_numeric_value.side_effect = ai_side_effect

        # 3. Mock Dataland Values (dataset.get_value_generic)
        # We use side_effect to return values based on category/field
        def dataland_side_effect(category, subcategory, field_name):
            if field_name == "scope1_ghg_emissions_in_tonnes":
                return 100.0  # Matches AI
            if field_name == "emissions_to_water_in_tonnes":
                return 80.0   # Mismatch (AI is 50.0)
            if field_name == "hazardous_and_radioactive_waste_in_tonnes":
                return None   # Empty in Dataland
            if field_name == "board_gender_diversity_supervisory_board_in_percent":
                return 30.0   # Exists in Dataland, but AI is None
            return None

        mock_dataset.get_value_generic.side_effect = dataland_side_effect

        # 4. Execute
        report = generator.generate_report(relevant_pages, mock_dataset)

        # 5. Assertions

        # --- CASE 1: MATCH (Scope 1) ---
        scope1 = report.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes
        assert scope1.verdict == QaReportDataPointVerdict.QAACCEPTED
        assert scope1.comment == "Values match"
        assert scope1.corrected_data.value is None

        # --- CASE 2: MISMATCH (Water) ---
        water = report.environmental.water.emissions_to_water_in_tonnes
        assert water.verdict == QaReportDataPointVerdict.QAREJECTED
        assert "Discrepancy" in water.comment
        # Should take the AI value as correction
        assert water.corrected_data.value == 50.0 

        # --- CASE 3: DATALAND EMPTY (Waste) ---
        waste = report.environmental.waste.hazardous_and_radioactive_waste_in_tonnes
        assert waste.verdict == QaReportDataPointVerdict.QAREJECTED
        assert "Dataland empty" in waste.comment
        assert waste.corrected_data.value == 10.0

        # --- CASE 4: AI EMPTY (Social) ---
        social = report.social.social_and_employee_matters.board_gender_diversity_supervisory_board_in_percent
        assert social.verdict == QaReportDataPointVerdict.QAREJECTED
        assert "AI found nothing" in social.comment
        # When AI finds nothing, quality is usually set to NoDataFound (based on your logic)
        assert social.corrected_data.quality == "NoDataFound"

    def test_generate_report_no_pages(self, mock_dataset: MagicMock) -> None:
        """Test that missing pages result in QANOTATTEMPTED."""
        generator = SfdrReportGenerator()
        
        # Pass None or empty string as relevant_pages
        report = generator.generate_report(None, mock_dataset)  # type: ignore

        # Check one field (they should all be the same)
        scope1 = report.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes
        
        assert scope1.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
        assert "No relevant pages" in scope1.comment

    @patch("dataland_qa_lab.review.report_generator.sfdr_report_generator.SFDRNumericValueGenerator")
    def test_compare_logic_both_empty(self, mock_numeric_gen: MagicMock, mock_dataset: MagicMock) -> None:
        """Test specific edge case: Both Dataland and AI are None."""
        generator = SfdrReportGenerator()
        
        mock_numeric_gen.get_generic_numeric_value.return_value = None
        mock_dataset.get_value_generic.return_value = None

        report = generator.generate_report("Pages content", mock_dataset)

        scope1 = report.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes
        assert scope1.verdict == QaReportDataPointVerdict.QAACCEPTED
        assert scope1.comment == "Both empty"