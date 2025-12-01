from __future__ import annotations

from urllib.parse import urljoin

import dataland_backend
import dataland_documents


class DatalandClient:
    """Provides an intuitive accessor for authenticated dataland API Instances.

    Attributes:
        dataland_url (str): The Dataland URL determined by the is_test_dataland switch.
        api_key (str): The API Key to use for authenticating against dataland.
    """

    dataland_url: str
    api_key: str

    def __init__(self, dataland_url: str, api_key: str) -> None:
        """Create a new DatalandClient.

        Args:
            dataland_url: The URL of the dataland instance to connect to.
            api_key: The API Key to use for authenticating against dataland.
        """
        self.dataland_url = dataland_url
        self.api_key = api_key

    @property
    def backend_client(self) -> dataland_backend.ApiClient:
        """Retrieves the client for accessing the backend API."""
        config = dataland_backend.Configuration(access_token=self.api_key, host=urljoin(self.dataland_url, "api"))
        return dataland_backend.ApiClient(config)

    @property
    def data_points_api(self) -> dataland_backend.DataPointControllerApi:
        """Function to run the document-controller API."""
        return dataland_backend.DataPointControllerApi(self.backend_client)

    @property
    def company_api(self) -> dataland_backend.CompanyDataControllerApi:
        """Function to run the company-data-controller API."""
        return dataland_backend.CompanyDataControllerApi(self.backend_client)

    @property
    def eu_taxonomy_nf_api(self) -> dataland_backend.EutaxonomyNonFinancialsDataControllerApi:
        """Function to run the eu-taxonomy-non-financials-data-controller API."""
        return dataland_backend.EutaxonomyNonFinancialsDataControllerApi(self.backend_client)

    @property
    def eu_taxonomy_nuclear_and_gas_api(self) -> dataland_backend.NuclearAndGasDataControllerApi:
        """Function to run the eu-taxonomy-nuclear-and-gas-data-controller API."""
        return dataland_backend.NuclearAndGasDataControllerApi(self.backend_client)

    @property
    def documents_client(self) -> dataland_documents.ApiClient:
        """Retrieves the client for accessing the documents API."""
        config = dataland_documents.Configuration(
            access_token=self.api_key, host=urljoin(self.dataland_url, "documents")
        )
        return dataland_documents.ApiClient(config)

    @property
    def documents_api(self) -> dataland_documents.DocumentControllerApi:
        """Function to run the document-controller API."""
        return dataland_documents.DocumentControllerApi(self.documents_client)

    @property
    def meta_api(self) -> dataland_backend.MetaDataControllerApi:
        """Function to run the meta-data-controller API."""
        return dataland_backend.MetaDataControllerApi(self.backend_client)
