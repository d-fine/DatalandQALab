from dataland_qa_lab.utils import config


def get_data_id_by_year(company_id: str, year: str) -> str:  # noqa: D103
    conf = config.get_config()
    dataland_client = conf.dataland_client

    dataset = dataland_client.eu_taxonomy_nuclear_and_gas_api.get_all_company_nuclear_and_gas_data(company_id=company_id)

    data_id = ""
    for t in range(len(dataset)):
        if (dataset[t].meta_info.reporting_period == year):
            data_id = dataset[t].meta_info.data_id
            break

    return data_id


def get_dataset_by_id(data_id: str) -> any:  # noqa: D103
    conf = config.get_config()
    dataland_client = conf.dataland_client

    return dataland_client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(data_id=data_id)
