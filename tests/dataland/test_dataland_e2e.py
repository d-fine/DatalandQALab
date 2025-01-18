from unittest.mock import ANY, MagicMock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_backend.models.extended_data_point_nuclear_and_gas_aligned_denominator import (
    ExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_backend.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_backend.models.nuclear_and_gas_aligned_denominator import NuclearAndGasAlignedDenominator
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_backend.models.nuclear_and_gas_environmental_objective import NuclearAndGasEnvironmentalObjective
from dataland_backend.models.nuclear_and_gas_general_taxonomy_aligned_denominator import (
    NuclearAndGasGeneralTaxonomyAlignedDenominator,
)

from dataland_qa_lab.review.dataset_reviewer import review_dataset


def create_document_intelligence_mock() -> AnalyzeResult:
    return AnalyzeResult(content="mocked content")


def create_mock_nuclear_and_gas_data() -> NuclearAndGasData:
    mock_data = MagicMock()
    mock_data.general = MagicMock()

    mock_data.general.general = MagicMock(
        nuclear_energy_related_activities_section426=ExtendedDataPointYesNo(value="Yes", data_source=None),
        nuclear_energy_related_activities_section427=ExtendedDataPointYesNo(value="No", data_source=None),
        nuclear_energy_related_activities_section428=ExtendedDataPointYesNo(value="Yes", data_source=None),
        fossil_gas_related_activities_section429=ExtendedDataPointYesNo(value="Yes", data_source=None),
        fossil_gas_related_activities_section430=ExtendedDataPointYesNo(value="Yes", data_source=None),
        fossil_gas_related_activities_section431=ExtendedDataPointYesNo(value="No", data_source=None),
    )

    mock_data.general.taxonomy_aligned_denominator = NuclearAndGasGeneralTaxonomyAlignedDenominator(
        nuclear_and_gas_taxonomy_aligned_capex_denominator=ExtendedDataPointNuclearAndGasAlignedDenominator(value=NuclearAndGasAlignedDenominator(
            taxonomyAlignedShareDenominatorNAndG426=NuclearAndGasEnvironmentalObjective()
        ))
    )

    return mock_data


@patch(
    "dataland_qa_lab.pages.text_to_doc_intelligence.extract_text_of_pdf",
    return_value=create_document_intelligence_mock(),
)
@patch("dataland_qa_lab.dataland.dataset_provider.get_dataset_by_id")
@patch("dataland_qa_lab.pages.pages_provider.get_relevant_pages_of_pdf")
@patch("dataland_qa_lab.utils.config.get_config")
@patch(
    "dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator.NuclearAndGasReportGenerator.generate_report"
)
def test_review_dataset_with_mocked_client(
    mock_generate_report: MagicMock,
    mock_get_config: MagicMock,
    mock_get_relevant_pages_of_pdf: MagicMock,
    mock_get_dataset_by_id: MagicMock,
    mock_extract_text_of_pdf: MagicMock,
) -> None:
    mock_config_instance = MagicMock()
    mock_get_config.return_value = mock_config_instance

    mock_dataland_client_instance = MagicMock()
    mock_config_instance.dataland_client = mock_dataland_client_instance

    mock_dataset = MagicMock()
    mock_dataset.data = create_mock_nuclear_and_gas_data()
    mock_get_dataset_by_id.return_value = mock_dataset

    mock_get_relevant_pages_of_pdf.return_value = {"content": "mocked content"}
    mock_generate_report.return_value = "mocked report"

    # Test review_dataset
    data_id = "mocked_data_id"
    review_dataset(data_id)

    mock_get_dataset_by_id.assert_called_once_with(data_id)
    mock_get_relevant_pages_of_pdf.assert_called_once()
    mock_generate_report.assert_called_once_with(relevant_pages=mock_extract_text_of_pdf.return_value, dataset=ANY)
    mock_dataland_client_instance.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report.assert_called_once_with(
        data_id=data_id, nuclear_and_gas_data=mock_generate_report.return_value
    )
