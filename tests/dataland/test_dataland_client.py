import dataland_qa_lab.dataland.get_data as qa
from dataland_qa_lab.utils import config


def test_dataland_connectivity() -> None:
    client = config.get_config().dataland_client
    resolved_companies = client.company_api.get_companies(chunk_size=1)

    company_id = "4423c691-0436-423f-abcb-0a08127ee848"
    year = "2024"
    qa.get_all_company_datasets(company_id=company_id)
    qa.get_data_id_by_year(company_id=company_id, year=year)
    qa.get_dataset_by_year(company_id=company_id, year=year)
    qa.get_value1_by_year(company_id=company_id, year=year)
    qa.get_datasource_reference_bytes(company_id=company_id, year=year)
    test_dataland = client.eu_taxonomy_nuclear_and_gas_api  # noqa: F841

    assert len(resolved_companies) > 0
