import json
from pathlib import Path

from dataland_backend.models.company_associated_data_nuclear_and_gas_data import (
    CompanyAssociatedDataNuclearAndGasData,
)

from dataland_qa_lab.utils import config


def upload_test_data() -> None:
    """Function to upload 10 test cases for EU Taxonomy Nuclear and Gas to Dataland."""
    pdf_path = Path("../data/pdfs/")
    json_path = Path("../data/jsons/")

    conf = config.get_config()
    dataland_client = conf.dataland_client

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
    for company, pdf_id in zip(companies, pdfs, strict=False):
        # if needed upload pdf file to dataland
        if not dataland_client.documents_api.get_document(document_id=pdf_id):
            pdf_file_path = pdf_path / f"{company}.pdf"
            pdf_content = pdf_file_path.read_bytes()

            dataland_client.documents_api.post_document(document=pdf_content)

        # get companyIDs of company to test
        if company == "eon":
            dataset = dataland_client.company_api.get_companies_by_search_string(
                search_string="E.ON SE", result_limit=1
            )
        elif company == "munichre":
            dataset = dataland_client.company_api.get_companies_by_search_string(
                search_string="Münchener Rückversicherungs-Gesellschaft Aktiengesellschaft in München", result_limit=1
            )
        else:
            dataset = dataland_client.company_api.get_companies_by_search_string(search_string=company, result_limit=1)

        company_id = dataset[0].company_id

        # change companyID in json file
        json_file_path = json_path / f"{company}.json"

        with json_file_path.open(encoding="utf-8") as f:
            json_data = json.load(f)
        json_data["companyId"] = company_id
        json_str = json.dumps(json_data, indent=4)
        json_file_path.write_text(json_str, encoding="utf-8")

        # if needed upload document
        if not dataland_client.eu_taxonomy_nuclear_and_gas_api.get_all_company_nuclear_and_gas_data(
            company_id=company_id
        ):
            nuclear_and_gas_data = CompanyAssociatedDataNuclearAndGasData.from_json(json_str)
            dataland_client.eu_taxonomy_nuclear_and_gas_api.post_company_associated_nuclear_and_gas_data(
                company_associated_data_nuclear_and_gas_data=nuclear_and_gas_data, bypass_qa=True
            )
