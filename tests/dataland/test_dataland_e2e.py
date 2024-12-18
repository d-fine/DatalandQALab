from pathlib import Path

from dataland_backend.models.yes_no import YesNo

from dataland_qa_lab.dataland.data_provider import (
    get_yes_no_values_by_data,
)
from dataland_qa_lab.dataland.provide_test_data import provide_test_data
from dataland_qa_lab.review.dataset_reviewer import review_dataset
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def test_e2e_valid_data() -> None:
    conf = config.get_config()
    dataland_client = conf.dataland_client

    pdf_path = Path.cwd() / "data" / "pdfs"
    json_path = Path.cwd() / "data" / "jsons"

    data_ids = provide_test_data(pdf_path=pdf_path, json_path=json_path, dataland_client=dataland_client)
    assert len(data_ids) > 0

    # test for 5 data ids
    for data_id in data_ids[:5]:
        data = dataland_client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(
            data_id=data_id
        )
        data_collection = NuclearAndGasDataCollection(dataset=data.data)

        # correct values for section 426 are taken from dataland
        assert (
            get_yes_no_values_by_data(data=data_collection)["nuclear_energy_related_activities_section426"] == YesNo.NO
        )

        assert review_dataset(data_id)
