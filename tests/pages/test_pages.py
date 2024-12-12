from dataland_qa_lab.pages import pages_provider
from tests.utils.provide_test_data_collection import provide_test_data_collection


def test_get_relevant_pages_yes_no() -> None:
    test_data_collection = provide_test_data_collection()

    page_numbers = pages_provider.get_relevant_pages_of_nuclear_and_gas_yes_no_questions(test_data_collection)

    assert {21, 22}.issubset(page_numbers)


def test_get_relevant_pages_numeric() -> None:
    test_data_collection = provide_test_data_collection()

    page_numbers = pages_provider.get_relevant_pages_of_numeric(test_data_collection)

    assert {31}.issubset(page_numbers)


def test_get_relevant_pages_of_pdf() -> None:
    test_data_collection = provide_test_data_collection()

    pages = pages_provider.get_relevant_pages_of_pdf(test_data_collection)

    assert pages is not None
