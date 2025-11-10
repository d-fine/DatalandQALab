from dataland_qa_lab.pages import pages_provider
from tests.utils.provide_test_data_collection import provide_test_data_collection


def test_get_nuclear_and_gas_page_numbers() -> None:
    test_data_collection = provide_test_data_collection()

    page_numbers = pages_provider.get_nuclear_and_gas_page_numbers(test_data_collection)

    assert {21, 22, 31}.issubset(set(page_numbers))


def test_get_relevant_pages_of_pdf() -> None:
    test_data_collection = provide_test_data_collection()

    pages = pages_provider.get_relevant_pages_of_pdf(test_data_collection)

    assert pages is not None
