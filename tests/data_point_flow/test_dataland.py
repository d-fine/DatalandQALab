import json
from unittest.mock import MagicMock, patch

import fitz 
import pytest

from dataland_qa_lab.data_point_flow import dataland, models


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
    # create a 2-page PDF using PyMuPDF
    doc = fitz.open()
    doc.new_page(width=100, height=100)
    doc.new_page(width=200, height=200)
    pdf_data = doc.tobytes()
    doc.close()

    mock_config.dataland_client.documents_api.get_document.return_value = pdf_data

    result_stream = await dataland.get_document("ref123", 2)

    # verify result is a 1-page PDF and has the expected page size
    out_doc = fitz.open(stream=result_stream.getvalue(), filetype="pdf")
    assert len(out_doc) == 1

    page = out_doc[0]
    assert page.rect.width == 200
    assert page.rect.height == 200
    out_doc.close()


@pytest.mark.asyncio
@patch("dataland_qa_lab.data_point_flow.dataland.config")
async def test_override_dataland_qa_calls_api(mock_config: MagicMock) -> None:
    """Test that override_dataland_qa calls the QA API correctly."""
    await dataland.override_dataland_qa(
        data_point_id="dp123",
        comment="Reasoning text",
        qa_status="QaAccepted",
        predicted_answer="Yes",
        data_source={},
    )

    mock_config.dataland_client.qa_api.datapoint_qa_controller_api.post_qa_report(
        data_point_id="dp123",
        qa_report_data_point_string={
            "comment": "Reasoning text",
            "verdict": "QaAccepted",
            "correctedData": json.dumps(
                {"value": "Yes", "quaility": "Incomplete", "comment": "program neural circuit", "dataSource": {}}
            ),
        },
    )