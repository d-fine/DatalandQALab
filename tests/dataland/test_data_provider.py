from dataland_backend.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_backend.models.nuclear_and_gas_general import NuclearAndGasGeneral
from dataland_backend.models.nuclear_and_gas_general_general import NuclearAndGasGeneralGeneral

from dataland_qa_lab.dataland.data_provider import DataProvider


def test_get_yes_no_values_by_data() -> None:
    test_dataset = NuclearAndGasData(
        general=NuclearAndGasGeneral(
            general=NuclearAndGasGeneralGeneral(
                nuclearEnergyRelatedActivitiesSection426=ExtendedDataPointYesNo(
                    value="Yes"
                ),
                fossilGasRelatedActivitiesSection430=ExtendedDataPointYesNo(
                    value="No"
                ),
            )
        )
    )

    provider = DataProvider()
    values = provider.get_yes_no_values_by_data(test_dataset)

    assert values[0] == "Yes"
    assert len(values) == 6
    assert values[2] is None
    assert values[4] == "No"
