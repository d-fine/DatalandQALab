from dataland_qa_lab.dataland import dataset_provider


def test_get_dataset() -> None:
    test_data_id = "9ae2300a-db98-4815-abee-152a24cd3039"
    dataset = dataset_provider.get_dataset_by_id(data_id=test_data_id)

    assert dataset.reporting_period is not None
