from dataland_qa_lab.dataland import dataset_provider


def test_get_dataset() -> None:
    test_data_id = "7b7c7ea2-7d74-4161-afc8-4aa6bcde66c7"
    dataset = dataset_provider.get_dataset_by_id(data_id=test_data_id)

    assert dataset.reporting_period is not None
