from dataland_qa_lab.dataland import data_provider
from tests.utils.provide_test_data_collection import provide_test_data_collection


def test_get_yes_no_values_by_data() -> None:
    test_data_collection = provide_test_data_collection()

    values = data_provider.get_yes_no_values_by_data(test_data_collection)

    assert values.get("nuclear_energy_related_activities_section426") == "Yes"
    assert len(values) == 6
    assert values.get("nuclear_energy_related_activities_section428") is None
    assert values.get("fossil_gas_related_activities_section430") == "No"


def test_get_datasources_of_dataset() -> None:
    test_data_collection = provide_test_data_collection()

    values = data_provider.get_datasources_of_nuclear_and_gas_yes_no_questions(test_data_collection)

    assert values.get("nuclear_energy_related_activities_section426").page == "21"
    assert len(values) == 6
    assert values.get("nuclear_energy_related_activities_section427") is None
    assert values.get("fossil_gas_related_activities_section431").tag_name is not None
    assert values.get("fossil_gas_related_activities_section431").file_name == "test-file"
