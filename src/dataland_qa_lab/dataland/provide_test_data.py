import json
from pathlib import Path

from dataland_backend.models.company_associated_data_nuclear_and_gas_data import (
    CompanyAssociatedDataNuclearAndGasData,
)

from dataland_qa_lab.utils import config


def provide_test_data(pdf_path: Path, json_path: Path) -> list[str]:
    """Upload 10 test cases.

    Upload 10 test cases for EU Taxonomy Nuclear and Gas to Dataland.

    :param pdf_path: absolute path to pdf files (required)
    :type pdf_path: Path
    :param json_path: absolute path to json files (required)
    :type json_path: Path
    :return: Returns a list containing the data ids of the test datasets.
    """
    # list of companies to test
    companies = ["concordia", "covestro", "deka", "enbw", "enel", "eon", "iberdrola", "munichre", "rwe", "total"]
    # list of ids of corresponding pdfs
    pdfs = [
        "0a8eebb9e32d3c0a32a1083699352018afcbbe39458ab8441cd0c8985a466a59",
        "ebff9ec3cf12e715cb6ee1c55a1295656a87e1716a9b536b4fbf2a1b9312260c",
        "b31dfa1143e9e518cfdacd95b2d4f6c531e50bc33c0dabbbe35cccfe14dd83f3",
        "9c0a555a29683aedd2cd50ff7e837181a7fbb2d1c567d336897e2356fc17a595",
        "a58354fd0d2969d7c3161d6ba273c9ba4814866c0fc8ec0e220dc4ee6e87753c",
        "4abdfd0764559831fdd2e972abab0f34bc7300c650f6f789beea10ecb7d20251",
        "3305bd49f340b73919de891d166f7492cd61f59a9efdc1b84a0720db1f846fc2",
        "e974e3f3675386f17b67af4a5b03ee5a0a313c4d0b07d719c2cf5cb715ccbeb3",
        "eb119227edc8c66d672785619522cd6045b2faf37e63796207799c0e40fa66be",
        "dba48e9f5e7e6fc9862dd95159960eb2a270d6975f2457f443ca422e7449e7d6",
    ]

    new_data_ids = []

    for company, pdf_id in zip(companies, pdfs, strict=False):
        # if needed upload pdf file to dataland
        upload_pdf(pdf_path=pdf_path, pdf_id=pdf_id, company=company)

        # get companyIDs of company to test
        company_id = get_company_id(company=company)

        # change companyID in json file
        json_file_path = json_path / f"{company}.json"

        with json_file_path.open(encoding="utf-8") as f:
            json_data = json.load(f)
        json_data["companyId"] = company_id
        json_str = json.dumps(json_data, indent=4)
        json_file_path.write_text(json_str, encoding="utf-8")

        # if needed upload dataset
        new_data_ids.append(upload_dataset(company_id=company_id, json_str=json_str))

    return new_data_ids


def upload_pdf(pdf_path: Path, pdf_id: str, company: str) -> None:
    """Uploads pdf file to dataland if needed.

    Checks if pdf file already exists on dataland and if not uploads it

    :param pdf_path: absolute path to pdf file (required)
    :type pdf_path: Path
    :param pdf_id: absolute path to json files (required)
    :type pdf_id: Path
    :param company: name of the company
    :type company: str
    """
    conf = config.get_config()
    dataland_client = conf.dataland_client

    if not dataland_client.documents_api.get_document(document_id=pdf_id):
        pdf_content = (pdf_path / f"{company}.pdf").read_bytes()

        dataland_client.documents_api.post_document(document=pdf_content)


def get_company_id(company: str) -> str:
    """Get company id of given company.

    Searches dataland for id for company with given name

    :param company: name of the company
    :type company: str
    :return: Returns the id of the given company
    """
    conf = config.get_config()
    dataland_client = conf.dataland_client

    if company == "eon":
        dataset = dataland_client.company_api.get_companies_by_search_string(search_string="E.ON SE", result_limit=1)
    elif company == "munichre":
        dataset = dataland_client.company_api.get_companies_by_search_string(
            search_string="Münchener Rückversicherungs-Gesellschaft Aktiengesellschaft in München", result_limit=1
        )
    else:
        dataset = dataland_client.company_api.get_companies_by_search_string(search_string=company, result_limit=1)

    return dataset[0].company_id


def upload_dataset(company_id: str, json_str: any) -> str:
    """Upload dataset.

    Upload dataset for EU Taxonomy Nuclear and Gas to Dataland.

    :param company_id: id of company dataset to be uploaded
    :type company_id: str
    :param json_str: json content to be uploaded
    :type json_str: Any
    :return: Returns data_ids with one appended id
    """
    conf = config.get_config()
    dataland_client = conf.dataland_client

    old_dataset = dataland_client.eu_taxonomy_nuclear_and_gas_api.get_all_company_nuclear_and_gas_data(
        company_id=company_id
    )
    if not old_dataset:
        nuclear_and_gas_data = CompanyAssociatedDataNuclearAndGasData.from_json(json_str)

        new_dataset = dataland_client.eu_taxonomy_nuclear_and_gas_api.post_company_associated_nuclear_and_gas_data(
            company_associated_data_nuclear_and_gas_data=nuclear_and_gas_data, bypass_qa=True
        )
        return new_dataset.data_id
    return old_dataset[0].meta_info.data_id