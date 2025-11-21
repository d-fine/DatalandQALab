from unittest.mock import MagicMock, patch, ANY
from dataclasses import dataclass, field
from typing import Optional

from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict
from dataland_qa_lab.review.dataset_reviewer import review_dataset


@dataclass
class MockDataSource:
    page: int = 5
    file_reference: str = "dummy.pdf"

@dataclass
class MockDataPoint:
    value: Optional[float] = None
    data_source: MockDataSource = field(default_factory=MockDataSource)

class MockSfdrData:
    """Simuliert die verschachtelte Struktur eines echten SFDR Datensatzes."""
    def __init__(self):
       
        self.environmental = type('Env', (), {})()
        
       
        self.environmental.greenhouse_gas_emissions = type('GHG', (), {})()
        self.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes = MockDataPoint(100.0)
        
    
        self.environmental.water = type('Water', (), {})()
        self.environmental.water.emissions_to_water_in_tonnes = MockDataPoint(50.0)
        
        self.environmental.waste = type('Waste', (), {})()
        self.environmental.waste.hazardous_and_radioactive_waste_in_tonnes = MockDataPoint(None) 
      
        self.social = type('Social', (), {})()
        self.social.social_and_employee_matters = type('Matters', (), {})()
        self.social.social_and_employee_matters.board_gender_diversity_supervisory_board_in_percent = MockDataPoint(30.0)

@dataclass
class MockDatasetContainer:
    data: MockSfdrData = field(default_factory=MockSfdrData)


# --- DER TEST ---

@patch("dataland_qa_lab.review.dataset_reviewer.update_reviewed_dataset_in_database") 
@patch("dataland_qa_lab.dataland.dataset_provider.get_sfdr_dataset_by_id") 
@patch("dataland_qa_lab.pages.text_to_doc_intelligence.get_markdown_from_dataset")
@patch("dataland_qa_lab.review.sfdr_numeric_value_generator.SFDRNumericValueGenerator.get_generic_numeric_value") # KI mocken
@patch("dataland_qa_lab.utils.config.get_config") 
def test_sfdr_report_generation_e2e(
    mock_config, 
    mock_get_ai_value, 
    mock_get_markdown, 
    mock_get_dataset,
    mock_db_update
):
    """
    Testet den kompletten SFDR Review Prozess (Logik-Ebene).
    Wir simulieren:
    - Daten aus Dataland (MockDatasetContainer)
    - Text aus PDF (Mock String)
    - Antworten der KI (Mock Values)
    Und prüfen, ob der generierte Report die richtigen Verdicts enthält.
    """
    
   
    mock_get_dataset.return_value = MockDatasetContainer()
    mock_get_markdown.return_value = "Dummy PDF Content"
    
    
    mock_api_client = MagicMock()
    mock_config.return_value.dataland_client = mock_api_client
    
   
    def ai_side_effect(text, kpi, unit):
        if "Scope 1" in kpi: return 100.0  
        if "Emissions to water" in kpi: return 99.0  
        if "Hazardous" in kpi: return 10.0 
        if "Board gender" in kpi: return 30.0 
        return None
    
    mock_get_ai_value.side_effect = ai_side_effect

    
    data_id = "test-sfdr-id-123"
   
    review_dataset(data_id, framework="sfdr", force_review=True)

    
    post_method = mock_api_client.sfdr_qa_api.post_sfdr_data_qa_report
    assert post_method.called, "Der Report wurde nicht an die API gesendet!"
    
    args, _ = post_method.call_args
    sent_data_id = args[0]
    sent_report = args[1] 
    
    assert sent_data_id == data_id
    
  
    
   
    scope1_result = sent_report.environmental.greenhouse_gas_emissions.scope1_ghg_emissions_in_tonnes
    assert scope1_result.verdict == QaReportDataPointVerdict.QAACCEPTED
    assert scope1_result.comment == "Values match"
    
    
    water_result = sent_report.environmental.water.emissions_to_water_in_tonnes
    assert water_result.verdict == QaReportDataPointVerdict.QAREJECTED
    assert "Discrepancy" in water_result.comment
    assert water_result.correctedData.value == 99.0 
    
   
    waste_result = sent_report.environmental.waste.hazardous_and_radioactive_waste_in_tonnes
    assert waste_result.verdict == QaReportDataPointVerdict.QAREJECTED
    assert "Dataland empty" in waste_result.comment
    assert waste_result.correctedData.value == 10.0