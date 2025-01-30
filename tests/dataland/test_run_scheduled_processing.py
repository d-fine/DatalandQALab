from unittest.mock import MagicMock, patch

from dataland_qa_lab.dataland.scheduled_processor import run_scheduled_processing


@patch("dataland_qa_lab.dataland.scheduled_processor.UnreviewedDatasets")
def test_run_scheduled_processing_unreviewed_datasets_error(mock_unreviewed_datasets: MagicMock) -> None:
    mock_unreviewed_datasets.side_effect = Exception("Error while creating UnreviewedDatasets")
    with pytest.raises(Exception) as context:  # noqa: PT011
        run_scheduled_processing(single_pass_e2e=True)
    assert str(context.value) == "Error while creating UnreviewedDatasets"
