from unittest.mock import Mock, patch

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
