import logging
from unittest.mock import MagicMock, Mock, patch

import pytest
from dataland_backend.models.company_associated_data_nuclear_and_gas_data import CompanyAssociatedDataNuclearAndGasData
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_backend.models.nuclear_and_gas_general import NuclearAndGasGeneral

from dataland_qa_lab.dataland import dataset_provider
from tests.utils import provide_test_dataset


@patch("dataland_qa_lab.dataland.dataset_provider.get_dataset_by_id")
def test_get_dataset(mock_get_dataset_by_id: Mock) -> None:
    mock_get_dataset_by_id.return_value = CompanyAssociatedDataNuclearAndGasData(
        companyId="90ba9a69-1612-42e1-aeff-681d3eb683ba",
        reportingPeriod="2023",
        data=NuclearAndGasData(
            general=NuclearAndGasGeneral(
                general=provide_test_dataset.create_template_1_reportframe(),
                taxonomyAlignedDenominator=provide_test_dataset.create_template_2_reportframe(),
                taxonomyAlignedNumerator=provide_test_dataset.create_template_3_reportframe(),
                taxonomyEligibleButNotAligned=provide_test_dataset.create_template_4_reportframe(),
                taxonomyNonEligible=provide_test_dataset.create_template_5_reportframe(),
            )
        ),
    )

    dataset = dataset_provider.get_dataset_by_id(data_id="test_data_id")

    assert dataset is not None


def test_get_dataset_by_id_error_case(caplog: pytest.LogCaptureFixture) -> None:
    """Test that an error is logged when an exception is raised while retrieving the dataset."""
    mock_client = MagicMock()
    mock_client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data.side_effect = Exception(
        "API error"
    )

    with patch("dataland_qa_lab.utils.config.get_config") as mock_get_config:
        mock_get_config.return_value.dataland_client = mock_client

        with caplog.at_level(logging.ERROR):
            dataset_provider.get_dataset_by_id("test_id")

        assert "Error retrieving dataset for the given data id test_id from dataland" in caplog.text
