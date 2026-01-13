import io
import json
from unittest.mock import MagicMock, patch

import pytest
from dataland_qa.models.qa_status import QaStatus
from pypdf import PdfReader, PdfWriter

from dataland_qa_lab.data_point_flow import (
    dataland,
    models,
)


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.dataland.config")
async def test_get_data_point_valid(mock_config: MagicMock) -> None:
    """Test fetching a valid data point."""
    mock_dp = MagicMock()
    mock_dp.data_point = json.dumps(
        {"dataSource": {"page": 1, "fileReference": "ref123", "fileName": "file.pdf"}, "value": "42"}
    )
    mock_dp.data_point_type = "number"

    mock_config.dataland_client.data_points_api.get_data_point.return_value = mock_dp

    result = await dataland.get_data_point("dp123")

    assert isinstance(result, models.DataPoint)
    assert result.data_point_id == "dp123"
    assert result.page == 1
    assert result.file_reference == "ref123"
    assert result.file_name == "file.pdf"
    assert result.value == "42"
    assert result.data_point_type == "number"


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.dataland.config")
async def test_get_data_point_missing_data_source(mock_config: MagicMock) -> None:
    """Test that get_data_point raises ValueError if dataSource is missing."""
    mock_dp = MagicMock()
    mock_dp.data_point = json.dumps({"value": "42"})
    mock_dp.data_point_type = "number"

    mock_config.dataland_client.data_points_api.get_data_point.return_value = mock_dp

    with pytest.raises(ValueError, match="missing dataSource"):
        await dataland.get_data_point("dp_missing")


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.dataland.config")
async def test_get_document_single_page(mock_config: MagicMock) -> None:
    """Test get_document extracts the correct page from a PDF."""
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_blank_page(width=200, height=200)

    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    pdf_data = pdf_bytes.read()

    mock_config.dataland_client.documents_api.get_document.return_value = pdf_data

    result_stream = await dataland.get_document("ref123", 2)

    reader = PdfReader(result_stream)
    assert len(reader.pages) == 1

    page = reader.pages[0]
    assert page.mediabox.width == 200
    assert page.mediabox.height == 200


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.dataland.config")
async def test_override_dataland_qa_calls_api(mock_config: MagicMock) -> None:
    """Test that override_dataland_qa calls the QA API correctly."""
    await dataland.override_dataland_qa("dp123", "Reasoning text", QaStatus.ACCEPTED)

    mock_config.dataland_client.qa_api.change_data_point_qa_status.assert_called_once_with(
        data_point_id="dp123", qa_status=QaStatus.ACCEPTED, comment="Reasoning text"
    )


@pytest.mark.asyncio
async def test_get_dependency_values_empty_list() -> None:
    """Test that empty dependency list returns empty dict."""
    result = await dataland.get_dependency_values("dp123", [])
    assert result == {}


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.dataland.config")
async def test_get_dependency_values_with_revenue(mock_config: MagicMock) -> None:
    """Test successful fetching of revenue dependency."""
    mock_config.dataland_client.data_points_api.get_data_point_meta_info.return_value = MagicMock(
        company_id="comp123", reporting_period="2023"
    )
    mock_config.dataland_client.meta_api.get_list_of_data_meta_info.return_value = [
        MagicMock(data_type="DataTypeEnum.SFDR", data_id="sfdr123")
    ]
    mock_sfdr_data = MagicMock()
    mock_sfdr_data.data.model_dump.return_value = {
        "environmental": {"greenhouse_gas_emissions": {"total_revenue_in_eur": 1000000}}
    }
    mock_config.dataland_client.sfdr_api.get_company_associated_sfdr_data.return_value = mock_sfdr_data

    result = await dataland.get_dependency_values("dp123", ["extendedDecimalTotalRevenueInEUR"])
    assert result == {"extendedDecimalTotalRevenueInEUR": "1000000"}


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.dataland.config")
async def test_get_dependency_values_no_sfdr_dataset(mock_config: MagicMock) -> None:
    """Test when no SFDR dataset exists."""
    mock_config.dataland_client.data_points_api.get_data_point_meta_info.return_value = MagicMock(
        company_id="comp123", reporting_period="2023"
    )
    mock_config.dataland_client.meta_api.get_list_of_data_meta_info.return_value = []

    result = await dataland.get_dependency_values("dp123", ["extendedDecimalTotalRevenueInEUR"])
    assert result == {"extendedDecimalTotalRevenueInEUR": "not available"}


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.dataland.config")
async def test_get_dependency_values_null_revenue(mock_config: MagicMock) -> None:
    """Test when revenue value is None/null."""
    mock_config.dataland_client.data_points_api.get_data_point_meta_info.return_value = MagicMock(
        company_id="comp123", reporting_period="2023"
    )
    mock_config.dataland_client.meta_api.get_list_of_data_meta_info.return_value = [
        MagicMock(data_type="DataTypeEnum.SFDR", data_id="sfdr123")
    ]
    mock_sfdr_data = MagicMock()
    mock_sfdr_data.data.model_dump.return_value = {
        "environmental": {"greenhouse_gas_emissions": {"total_revenue_in_eur": None}}
    }
    mock_config.dataland_client.sfdr_api.get_company_associated_sfdr_data.return_value = mock_sfdr_data

    result = await dataland.get_dependency_values("dp123", ["extendedDecimalTotalRevenueInEUR"])
    assert result == {"extendedDecimalTotalRevenueInEUR": "not available"}


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.dataland.config")
async def test_get_dependency_values_api_error(mock_config: MagicMock) -> None:
    """Test when API calls fail."""
    mock_config.dataland_client.data_points_api.get_data_point_meta_info.side_effect = AttributeError("API error")

    result = await dataland.get_dependency_values("dp123", ["extendedDecimalTotalRevenueInEUR"])
    assert result == {"extendedDecimalTotalRevenueInEUR": "not available"}


def test_find_sfdr_dataset_id_found() -> None:
    """Test finding SFDR dataset ID."""
    datasets = [
        MagicMock(data_type="DataTypeEnum.OTHER", data_id="other123"),
        MagicMock(data_type="DataTypeEnum.SFDR", data_id="sfdr123"),
    ]
    result = dataland._find_sfdr_dataset_id(datasets)
    assert result == "sfdr123"


def test_find_sfdr_dataset_id_not_found() -> None:
    """Test when SFDR dataset doesn't exist."""
    datasets = [MagicMock(data_type="DataTypeEnum.OTHER", data_id="other123")]
    result = dataland._find_sfdr_dataset_id(datasets)
    assert result is None


def test_extract_dependency_values_success() -> None:
    """Test extracting revenue from data dict."""
    data_dict = {"environmental": {"greenhouse_gas_emissions": {"total_revenue_in_eur": 500000}}}
    result = dataland._extract_dependency_values(["extendedDecimalTotalRevenueInEUR"], data_dict, "not available")
    assert result == {"extendedDecimalTotalRevenueInEUR": "500000"}


def test_extract_dependency_values_missing_key() -> None:
    """Test when revenue key is missing."""
    data_dict = {"environmental": {}}
    result = dataland._extract_dependency_values(["extendedDecimalTotalRevenueInEUR"], data_dict, "not available")
    assert result == {"extendedDecimalTotalRevenueInEUR": "not available"}


def test_extract_dependency_values_unknown_field() -> None:
    """Test with unknown field name."""
    data_dict = {"environmental": {"greenhouse_gas_emissions": {"total_revenue_in_eur": 500000}}}
    result = dataland._extract_dependency_values(["unknownField"], data_dict, "not available")
    assert result == {"unknownField": "not available"}
