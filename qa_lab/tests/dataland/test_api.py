import io
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from qa_lab.dataland import api


class MockConf:
    dataland_url = "https://fake-dataland.com"
    dataland_api_key = "fake-key"


# Patch get_config globally in the module
@pytest.fixture(autouse=True)
def patch_get_config() -> Generator[None, Any, Any]:
    """Test fixture to patch get_config globally in the module."""
    with patch("qa_lab.dataland.api.get_config", return_value=MockConf()):
        yield


@patch("qa_lab.dataland.api.requests.request")
def test_get_pending_datasets_success(mock_request: MagicMock) -> None:
    """Test that get_pending_datasets returns parsed data on success."""
    expected_data = [{"dataId": "ds1"}, {"dataId": "ds2"}]
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = expected_data

    result = api.get_pending_datasets()
    assert result == expected_data
    mock_request.assert_called_once()
    assert "qa/datasets" in mock_request.call_args[0][1]


@patch("qa_lab.dataland.api.requests.request")
def test_get_pending_datasets_failure(mock_request: MagicMock) -> None:
    """Test that get_pending_datasets returns empty list on failure."""
    mock_request.return_value.status_code = 500
    result = api.get_pending_datasets()
    assert result == []


@patch("qa_lab.dataland.api.requests.request")
def test_get_dataset_data_points_success(mock_request: MagicMock) -> None:
    """Test that get_dataset_data_points returns parsed data on success."""
    dataset_id = "ds1"
    expected_data = {"dp1": "data1", "dp2": "data2"}
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = expected_data

    result = api.get_dataset_data_points(dataset_id)
    assert result == expected_data
    assert f"/api/metadata/{dataset_id}/data-points" in mock_request.call_args[0][1]


@patch("qa_lab.dataland.api.requests.request")
def test_set_dataset_status_calls_post(mock_request: MagicMock) -> None:
    """Test that set_dataset_status makes the correct POST request."""
    dataset_id = "ds1"
    qa_status = "Accepted"

    # Call the function
    api.set_dataset_status(dataset_id, qa_status)

    # The URL that should have been called
    expected_url = (
        f"{api.config.dataland_url}/qa/datasets/{dataset_id}?overwriteDataPointQaStatus=false&qaStatus={qa_status}"
    )

    # Assert the call
    mock_request.assert_called_once()
    call_args = mock_request.call_args
    method_called, url_called = call_args[0][0], call_args[0][1]

    assert method_called == "POST"
    assert url_called == expected_url
    # headers object reference may differ, just check keys and values
    called_headers = call_args[1]["headers"]
    assert called_headers["Authorization"] == f"Bearer {api.config.dataland_api_key}"
    assert called_headers["accept"] == "application/json"


@patch("qa_lab.dataland.api.requests.request")
def test_get_data_point_success(mock_request: MagicMock) -> None:
    """Test that get_data_point returns parsed data point on success."""
    data_point_id = "dp1"
    raw_data = {"dataPoint": '{"value": "42"}'}
    mock_request.return_value.status_code = 200
    mock_request.return_value.json.return_value = raw_data

    result = api.get_data_point(data_point_id)
    assert result["dataPoint"]["value"] == "42"


@patch("qa_lab.dataland.api.requests.request")
def test_get_data_point_failure(mock_request: MagicMock) -> None:
    """Test that get_data_point returns empty dict on failure."""
    data_point_id = "dp1"
    mock_request.return_value.status_code = 500
    result = api.get_data_point(data_point_id)
    assert result == {}


@patch("qa_lab.dataland.api.requests.request")
@patch("qa_lab.dataland.api.pypdf.PdfReader")
@patch("qa_lab.dataland.api.pypdf.PdfWriter")
def test_get_document_extracts_pages(mock_writer: MagicMock, mock_reader: MagicMock, mock_request: MagicMock) -> None:
    """Test that get_document extracts specified pages from a PDF."""
    file_reference = "file123"
    pdf_content = b"%PDF-1.4 fake pdf content"
    mock_request.return_value.content = pdf_content

    mock_page = MagicMock()
    mock_reader.return_value.pages = [mock_page, mock_page, mock_page]

    mock_output_pdf = MagicMock()
    mock_writer.return_value = mock_output_pdf

    pages_to_extract = [1, 3]
    result_stream = api.get_document(file_reference, pages_to_extract)
    assert isinstance(result_stream, io.BytesIO)
    mock_writer.return_value.add_page.assert_called()  # called at least once


@patch("qa_lab.dataland.api.requests.request")
def test_update_data_point_qa_report_calls_post(mock_request: MagicMock) -> None:
    """Test that update_data_point_qa_report makes the correct POST request."""
    data_point_id = "dp1"
    qa_status = "Accepted"
    comment = "Test comment"

    api.update_data_point_qa_report(data_point_id, qa_status, comment)

    expected_url = f"{api.config.dataland_url}/qa/data-points/{data_point_id}?qaStatus={qa_status}&comment={comment}"

    # Check that requests.request was called
    mock_request.assert_called_once()
    method_called, url_called = mock_request.call_args[0][0], mock_request.call_args[0][1]
    headers_called = mock_request.call_args[1]["headers"]

    assert method_called == "POST"
    assert url_called == expected_url
    # Check headers content
    assert headers_called["Authorization"] == f"Bearer {api.config.dataland_api_key}"
    assert headers_called["accept"] == "application/json"
