from pathlib import Path

from dataland_qa_lab.dataland.data_provider import (
    get_yes_no_values_by_data,
)
from dataland_qa_lab.dataland.provide_test_data import provide_test_data
from dataland_qa_lab.pages.pages_provider import get_relevant_pages_of_pdf
from dataland_qa_lab.pages.text_to_doc_intelligence import extract_text_of_pdf
from dataland_qa_lab.review.yes_no_value_generator import extract_yes_no_template
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def test_e2e_valid_data() -> None:
    conf = config.get_config()
    dataland_client = conf.dataland_client

    pdf_path = Path.cwd() / "data" / "pdfs"
    json_path = Path.cwd() / "data" / "jsons"

    data_ids = provide_test_data(pdf_path=pdf_path, json_path=json_path, dataland_client=dataland_client)
    assert len(data_ids) > 0

    yes_no_values_dataland = []
    extracted_yes_no_values = []

    # currently only test for yes no values
    for data_id in data_ids:
        data = dataland_client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(
            data_id=data_id
        )
        data_collection = NuclearAndGasDataCollection(dataset=data.data)

        # get values on Dataland
        yes_no_values_dataland.append(get_yes_no_values_by_data(data=data_collection))

        # get values from AI
        pdf_reader = get_relevant_pages_of_pdf(data_collection)
        text_of_page = extract_text_of_pdf(pdf_reader)
        extracted_yes_no_values.append(extract_yes_no_template(text_of_page))

    # values in dataland and extracted should be equal with a certain percentage
    threshold = 0.9

    total_sections = 0
    matching_sections = 0

    for dataland_dict, extracted_dict in zip(yes_no_values_dataland, extracted_yes_no_values, strict=False):
        for key in dataland_dict:
            total_sections += 1
            if dataland_dict[key] == extracted_dict[key]:
                matching_sections += 1

    matching_ratio = matching_sections / total_sections
    assert matching_ratio >= threshold
