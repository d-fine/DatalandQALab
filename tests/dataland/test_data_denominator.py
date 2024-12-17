from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.dataland.dataset_provider import get_dataset_by_id
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def create_data_collection(dataset_id: str) -> None:
    dataset = get_dataset_by_id(dataset_id).data
    test_data_collection = NuclearAndGasDataCollection(dataset)
    return test_data_collection


def test_get_taxonomy_aligned_revenue_denominator_values_by_data(test_data_collection: NuclearAndGasDataCollection) -> None:
    revenue_dominator_values = data_provider.get_taxonomy_aligned_revenue_denominator_values_by_data(
        test_data_collection
    )
    print("Revenue Denominator: ")
    print(revenue_dominator_values)
    print("\n")


def test_get_taxonomy_aligned_capex_denominator_values_by_data(test_data_collection: NuclearAndGasDataCollection) -> None:
    capex_dominator_values = data_provider.get_taxonomy_aligned_capex_denominator_values_by_data(
        test_data_collection
    )
    print("Capex Denominator: ")
    print(capex_dominator_values)
    print("\n")


def test_get_taxonomy_aligned_revenue_numerator_values_by_data(test_data_collection: NuclearAndGasDataCollection) -> None:
    revenue_numerator_values = data_provider.get_taxonomy_aligned_revenue_numerator_values_by_data(
        test_data_collection
    )
    print("Revenue Numerator: ")
    print(revenue_numerator_values)
    print("\n")


def test_get_taxonomy_aligned_capex_numerator_values_by_data(test_data_collection: NuclearAndGasDataCollection) -> None:
    capex_numerator_values = data_provider.get_taxonomy_aligned_capex_numerator_values_by_data(
        test_data_collection
    )
    print("Capex Numerator: ")
    print(capex_numerator_values)
    print("\n")


def test_taxonomy_eligible_but_not_aligned_revenue_values_by_data(test_data_collection: NuclearAndGasDataCollection) -> None:
    eligible_not_aligned_revenue_values = data_provider.get_taxonomy_eligible_but_not_aligned_revenue_values_by_data(
        test_data_collection
    )
    print("Eligible but not aligned Revenue: ")
    print(eligible_not_aligned_revenue_values)
    print("\n")


def test_taxonomy_eligible_but_not_aligned_capex_values_by_data(test_data_collection: NuclearAndGasDataCollection) -> None:
    eligible_not_aligned_capex_values = data_provider.get_taxonomy_eligible_but_not_aligned_capex_values_by_data(
        test_data_collection
    )
    print("Eligible but not aligned Capex: ")
    print(eligible_not_aligned_capex_values)
    print("\n")


def test_taxonomy_non_eligible_revenue_values_by_data(test_data_collection: NuclearAndGasDataCollection) -> None:
    non_eligible_revenue_values = data_provider.get_taxonomy_non_eligible_revenue_values_by_data(
        test_data_collection
    )
    print("Non Eligible Revenue: ")
    print(non_eligible_revenue_values)
    print("\n")


def test_taxonomy_non_eligible_capex_values_by_data(test_data_collection: NuclearAndGasDataCollection) -> None:
    non_eligible_capex_values = data_provider.get_taxonomy_non_eligible_capex_values_by_data(
        test_data_collection
    )
    print("Non Eligible Capex: ")
    print(non_eligible_capex_values)
    print("\n")


if __name__ == "__main__":
    test_data_collection = create_data_collection("fae59f2e-c438-4457-9a74-55c0db006fee")
    # Template 2
    test_get_taxonomy_aligned_revenue_denominator_values_by_data(test_data_collection)
    test_get_taxonomy_aligned_capex_denominator_values_by_data(test_data_collection)
    # Template 3
    test_get_taxonomy_aligned_revenue_numerator_values_by_data(test_data_collection)
    test_get_taxonomy_aligned_capex_numerator_values_by_data(test_data_collection)
    # Template 4
    test_taxonomy_eligible_but_not_aligned_revenue_values_by_data(test_data_collection)
    test_taxonomy_eligible_but_not_aligned_capex_values_by_data(test_data_collection)
    # Template 5
    test_taxonomy_non_eligible_revenue_values_by_data(test_data_collection)
    test_taxonomy_non_eligible_capex_values_by_data(test_data_collection)
