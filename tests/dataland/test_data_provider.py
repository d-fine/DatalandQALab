import pytest

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.dataland.dataset_provider import get_dataset_by_id
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection
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


def test_get_taxonomy_aligned_revenue_denominator_values_by_data(
    test_data_collection: NuclearAndGasDataCollection,
) -> None:
    revenue_denominator_values = data_provider.get_taxonomy_aligned_revenue_denominator_values_by_data(
        test_data_collection
    )
    assert len(revenue_denominator_values) > 0
    assert "taxonomy_aligned_share_denominator" in revenue_denominator_values
    assert revenue_denominator_values["taxonomy_aligned_share_denominator"] is not None


def test_get_taxonomy_aligned_capex_denominator_values_by_data(
    test_data_collection: NuclearAndGasDataCollection,
) -> None:
    capex_denominator_values = data_provider.get_taxonomy_aligned_capex_denominator_values_by_data(test_data_collection)
    assert len(capex_denominator_values) > 0
    assert "taxonomy_aligned_share_denominator" in capex_denominator_values
    assert capex_denominator_values["taxonomy_aligned_share_denominator"] is not None


def test_get_taxonomy_aligned_revenue_numerator_values_by_data(
    test_data_collection: NuclearAndGasDataCollection,
) -> None:
    revenue_numerator_values = data_provider.get_taxonomy_aligned_revenue_numerator_values_by_data(test_data_collection)
    assert len(revenue_numerator_values) > 0
    assert "taxonomy_aligned_share_numerator" in revenue_numerator_values
    assert revenue_numerator_values["taxonomy_aligned_share_numerator"] is not None


def test_get_taxonomy_aligned_capex_numerator_values_by_data(test_data_collection: NuclearAndGasDataCollection) -> None:
    capex_numerator_values = data_provider.get_taxonomy_aligned_capex_numerator_values_by_data(test_data_collection)
    assert len(capex_numerator_values) > 0
    assert "taxonomy_aligned_share_numerator" in capex_numerator_values
    assert capex_numerator_values["taxonomy_aligned_share_numerator"] is not None


def test_taxonomy_eligible_but_not_aligned_revenue_values_by_data(
    test_data_collection: NuclearAndGasDataCollection,
) -> None:
    eligible_not_aligned_revenue_values = data_provider.get_taxonomy_eligible_but_not_aligned_revenue_values_by_data(
        test_data_collection
    )
    assert len(eligible_not_aligned_revenue_values) > 0
    assert "taxonomy_eligible_but_not_aligned_share" in eligible_not_aligned_revenue_values
    assert eligible_not_aligned_revenue_values["taxonomy_eligible_but_not_aligned_share"] is not None


def test_taxonomy_eligible_but_not_aligned_capex_values_by_data(
    test_data_collection: NuclearAndGasDataCollection,
) -> None:
    eligible_not_aligned_capex_values = data_provider.get_taxonomy_eligible_but_not_aligned_capex_values_by_data(
        test_data_collection
    )
    assert len(eligible_not_aligned_capex_values) > 0
    assert "taxonomy_eligible_but_not_aligned_share" in eligible_not_aligned_capex_values
    assert eligible_not_aligned_capex_values["taxonomy_eligible_but_not_aligned_share"] is not None


def test_taxonomy_non_eligible_revenue_values_by_data(test_data_collection: NuclearAndGasDataCollection) -> None:
    non_eligible_revenue_values = data_provider.get_taxonomy_non_eligible_revenue_values_by_data(test_data_collection)
    assert len(non_eligible_revenue_values) > 0
    assert "taxonomy_non_eligible_share" in non_eligible_revenue_values
    assert non_eligible_revenue_values["taxonomy_non_eligible_share"] is not None


def test_taxonomy_non_eligible_capex_values_by_data(test_data_collection: NuclearAndGasDataCollection) -> None:
    non_eligible_capex_values = data_provider.get_taxonomy_non_eligible_capex_values_by_data(test_data_collection)
    assert len(non_eligible_capex_values) > 0
    assert "taxonomy_non_eligible_share" in non_eligible_capex_values
    assert non_eligible_capex_values["taxonomy_non_eligible_share"] is not None


@pytest.fixture
def test_data_collection() -> NuclearAndGasDataCollection:
    dataset_id = "fae59f2e-c438-4457-9a74-55c0db006fee"
    dataset = get_dataset_by_id(dataset_id).data
    return NuclearAndGasDataCollection(dataset)
