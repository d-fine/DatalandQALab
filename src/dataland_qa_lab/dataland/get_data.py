from dataland_qa_lab.utils import config

def get_data_set_by_year(company_id: str, year: str) -> str:
    conf = config.get_config()
    dataland_client = conf.dataland_client

    dataset = dataland_client.eu_taxonomy_nuclear_and_gas_api.get_all_company_nuclear_and_gas_data(company_id=company_id)

    # Eintragen aus welcher Periode man das Dataset haben will -> In diesem Fall 2024
    data_id = "test"
    for t in range(len(dataset)):
        if (dataset[t].meta_info.reporting_period == year):
            data_id = dataset[t].meta_info.data_id
            break

    return data_id
