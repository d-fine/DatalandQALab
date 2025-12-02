from unittest.mock import PropertyMock, patch, MagicMock

import pytest

from dataland_qa_lab.dataland.dataland_client import DatalandClient
from dataland_qa_lab.utils import config


@pytest.fixture
def client() -> None:
    """Client fixture"""
    return DatalandClient(dataland_url="https://test.dataland.com", api_key="fake_key")


def test_dataland_connectivity() -> None:
    """Test dataland connectivity"""
    client = config.get_config().dataland_client
    resolved_companies = client.company_api.get_companies(chunk_size=1)
    assert len(resolved_companies) > 0


@patch("dataland_qa_lab.dataland.dataland_client.dataland_backend.ApiClient")
@patch("dataland_qa_lab.dataland.dataland_client.dataland_backend.Configuration")
def test_backend_client(mock_config: MagicMock, mock_api_client: MagicMock, client: MagicMock) -> None:
    """Test backend client"""
    mock_api_client.return_value = "backend_client"
    result = client.backend_client
    mock_config.assert_called_once_with(access_token="fake_key", host="https://test.dataland.com/api")
    mock_api_client.assert_called_once_with(mock_config.return_value)
    assert result == "backend_client"


@patch("dataland_qa_lab.dataland.dataland_client.dataland_backend.DataPointControllerApi")
def test_data_points_api(mock_api: MagicMock, client: MagicMock) -> None:
    """Test the data points api property."""
    mock_api.return_value = "data_points_api_instance"
    with patch.object(DatalandClient, "backend_client", new_callable=PropertyMock) as mock_backend:
        mock_backend.return_value = "mocked_backend_client"
        result = client.data_points_api
    assert result == "data_points_api_instance"
    mock_api.assert_called_once_with("mocked_backend_client")


@patch("dataland_qa_lab.dataland.dataland_client.dataland_backend.CompanyDataControllerApi")
def test_company_api(mock_api: MagicMock, client: MagicMock) -> None:
    """Test the company api property."""
    mock_api.return_value = "company_api_instance"
    with patch.object(DatalandClient, "backend_client", new_callable=PropertyMock) as mock_backend:
        mock_backend.return_value = "mocked_backend_client"
        result = client.company_api
    assert result == "company_api_instance"
    mock_api.assert_called_once_with("mocked_backend_client")


@patch("dataland_qa_lab.dataland.dataland_client.dataland_backend.EutaxonomyNonFinancialsDataControllerApi")
def test_eu_taxonomy_nf_api(mock_api: MagicMock, client: MagicMock) -> None:
    """Test the EU taxonomy non-financials api property."""
    mock_api.return_value = "eu_taxonomy_nf_instance"
    with patch.object(DatalandClient, "backend_client", new_callable=PropertyMock) as mock_backend:
        mock_backend.return_value = "mocked_backend_client"
        result = client.eu_taxonomy_nf_api
    assert result == "eu_taxonomy_nf_instance"
    mock_api.assert_called_once_with("mocked_backend_client")


@patch("dataland_qa_lab.dataland.dataland_client.dataland_backend.NuclearAndGasDataControllerApi")
def test_eu_taxonomy_nuclear_and_gas_api(mock_api: MagicMock, client: MagicMock) -> None:
    """Test the EU taxonomy nuclear and gas api property."""
    mock_api.return_value = "nuclear_gas_api_instance"
    with patch.object(DatalandClient, "backend_client", new_callable=PropertyMock) as mock_backend:
        mock_backend.return_value = "mocked_backend_client"
        result = client.eu_taxonomy_nuclear_and_gas_api
    assert result == "nuclear_gas_api_instance"
    mock_api.assert_called_once_with("mocked_backend_client")


@patch("dataland_qa_lab.dataland.dataland_client.dataland_documents.ApiClient")
@patch("dataland_qa_lab.dataland.dataland_client.dataland_documents.Configuration")
def test_documents_client(mock_config: MagicMock, mock_api_client: MagicMock, client: MagicMock) -> None:
    """Test the documents client property."""
    mock_api_client.return_value = "documents_client_instance"
    result = client.documents_client
    mock_config.assert_called_once_with(access_token="fake_key", host="https://test.dataland.com/documents")
    mock_api_client.assert_called_once_with(mock_config.return_value)
    assert result == "documents_client_instance"


@patch("dataland_qa_lab.dataland.dataland_client.dataland_documents.DocumentControllerApi")
def test_documents_api(mock_api: MagicMock, client: MagicMock) -> None:
    """Test the documents api property."""
    mock_api.return_value = "documents_api_instance"
    with patch.object(DatalandClient, "documents_client", new_callable=PropertyMock) as mock_docs_client:
        mock_docs_client.return_value = "mocked_documents_client"
        result = client.documents_api
    assert result == "documents_api_instance"
    mock_api.assert_called_once_with("mocked_documents_client")


@patch("dataland_qa_lab.dataland.dataland_client.dataland_backend.MetaDataControllerApi")
def test_meta_api(mock_api: MagicMock, client: MagicMock) -> None:
    """Test the meta api property."""
    mock_api.return_value = "meta_api_instance"
    with patch.object(DatalandClient, "backend_client", new_callable=PropertyMock) as mock_backend:
        mock_backend.return_value = "mocked_backend_client"
        result = client.meta_api
    assert result == "meta_api_instance"
    mock_api.assert_called_once_with("mocked_backend_client")


@patch("dataland_qa_lab.dataland.dataland_client.dataland_qa.ApiClient")
@patch("dataland_qa_lab.dataland.dataland_client.dataland_qa.Configuration")
def test_qa_client(mock_config: MagicMock, mock_api_client: MagicMock, client: MagicMock) -> None:
    """Test the QA client property."""
    mock_api_client.return_value = "qa_client_instance"
    result = client.qa_client
    mock_config.assert_called_once_with(access_token="fake_key", host="https://test.dataland.com/qa")
    mock_api_client.assert_called_once_with(mock_config.return_value)
    assert result == "qa_client_instance"


@patch("dataland_qa_lab.dataland.dataland_client.dataland_qa.QaControllerApi")
def test_qa_api(mock_api: MagicMock, client: MagicMock) -> None:
    """Test the QA api property."""
    mock_api.return_value = "qa_api_instance"
    with patch.object(DatalandClient, "qa_client", new_callable=PropertyMock) as mock_qa_client:
        mock_qa_client.return_value = "mocked_qa_client"
        result = client.qa_api
    assert result == "qa_api_instance"
    mock_api.assert_called_once_with("mocked_qa_client")


@patch("dataland_qa_lab.dataland.dataland_client.dataland_qa.EutaxonomyNonFinancialsDataQaReportControllerApi")
def test_eu_taxonomy_nf_qa_api(mock_api: MagicMock, client: MagicMock) -> None:
    """Test the api client"""
    mock_api.return_value = "eu_nf_qa_api_instance"
    with patch.object(DatalandClient, "qa_client", new_callable=PropertyMock) as mock_qa_client:
        mock_qa_client.return_value = "mocked_qa_client"
        result = client.eu_taxonomy_nf_qa_api
    assert result == "eu_nf_qa_api_instance"
    mock_api.assert_called_once_with("mocked_qa_client")


@patch("dataland_qa_lab.dataland.dataland_client.dataland_qa.NuclearAndGasDataQaReportControllerApi")
def test_eu_taxonomy_nuclear_gas_qa_api(mock_api: MagicMock, client: MagicMock) -> None:
    """Tests the api client"""
    mock_api.return_value = "nuclear_gas_qa_api_instance"
    with patch.object(DatalandClient, "qa_client", new_callable=PropertyMock) as mock_qa_client:
        mock_qa_client.return_value = "mocked_qa_client"
        result = client.eu_taxonomy_nuclear_gas_qa_api
    assert result == "nuclear_gas_qa_api_instance"
    mock_api.assert_called_once_with("mocked_qa_client")
