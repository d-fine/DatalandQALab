from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from dataland_qa_lab.bin.server import app
from dataland_qa_lab.data_point_flow.scheduler import run_scheduled_processing


@pytest.fixture
def mocks():  # noqa: ANN201
    """Prepare all common patches and mocks."""
    with (
        patch("dataland_qa_lab.data_point_flow.scheduler.logger") as logger,
        patch("dataland_qa_lab.data_point_flow.scheduler.config") as config,
        patch("dataland_qa_lab.data_point_flow.scheduler.database_engine") as db_engine,
        patch("dataland_qa_lab.data_point_flow.scheduler.database_tables") as db_tables,
        patch("dataland_qa_lab.data_point_flow.scheduler.review") as review,
        patch("dataland_qa_lab.data_point_flow.scheduler.slack") as slack,
        patch("asyncio.run") as asyncio_run,
    ):
        yield {
            "logger": logger,
            "config": config,
            "db_engine": db_engine,
            "db_tables": db_tables,
            "review": review,
            "slack": slack,
            "asyncio_run": asyncio_run,
        }


def test_no_unreviewed_datasets(mocks: MagicMock) -> None:
    """Should do nothing when QA API reports no datasets."""
    config = mocks["config"]
    db_engine = mocks["db_engine"]

    config.dataland_client.qa_api.get_number_of_pending_datasets.return_value = 0
    config.dataland_client.qa_api.get_info_on_datasets.return_value = []

    run_scheduled_processing()

    db_engine.add_entity.assert_not_called()
    mocks["slack"].send_slack_message.assert_not_called()


def test_skip_already_processed_dataset(mocks: MagicMock) -> None:
    """Should skip datasets already in the DB."""
    config = mocks["config"]
    db_engine = mocks["db_engine"]

    dataset = MagicMock()
    dataset.data_id = "D1"

    config.dataland_client.qa_api.get_number_of_pending_datasets.return_value = 1
    config.dataland_client.qa_api.get_info_on_datasets.return_value = [dataset]

    db_engine.get_entity.return_value = True

    run_scheduled_processing()

    mocks["asyncio_run"].assert_not_called()
    db_engine.add_entity.assert_not_called()


def test_process_dataset_and_classify_results(mocks: MagicMock) -> None:
    """Test processing a dataset and classifying results."""
    config = mocks["config"]
    review = mocks["review"]
    slack = mocks["slack"]
    db_engine = mocks["db_engine"]
    db_tables = mocks["db_tables"]
    asyncio_run = mocks["asyncio_run"]

    class ValidatedDatapoint:
        def __init__(self, data_point_id: str, qa_status: str) -> None:
            """Initialize ValidatedDatapoint."""
            self.data_point_id = data_point_id
            self.qa_status = qa_status

    class CannotValidateDatapoint:
        def __init__(self, data_point_id: str) -> None:
            """Initialize CannotValidateDatapoint."""
            self.data_point_id = data_point_id

    review.models.ValidatedDatapoint = ValidatedDatapoint
    review.models.CannotValidateDatapoint = CannotValidateDatapoint

    class ReviewedDataset:
        def __init__(
            self, data_id: str, review_start_time: int, review_end_time: int, review_completed: bool, report_id: str
        ) -> None:
            """Initialize ReviewedDataset."""
            self.data_id = data_id
            self.review_start_time = review_start_time
            self.review_end_time = review_end_time
            self.review_completed = review_completed
            self.report_id = report_id

    db_tables.ReviewedDataset = ReviewedDataset

    dataset = MagicMock()
    dataset.data_id = "D123"
    config.dataland_client.qa_api.get_number_of_pending_datasets.return_value = 1
    config.dataland_client.qa_api.get_info_on_datasets.return_value = [dataset]

    db_engine.get_entity.return_value = False

    config.dataland_client.meta_api.get_contained_data_points.return_value = {
        "k1": "dp1",
        "k2": "dp2",
        "k3": "dp3",
    }

    accepted_dp = ValidatedDatapoint("dp1", "QaAccepted")
    rejected_dp = ValidatedDatapoint("dp2", "QaRejected")
    cannot_dp = CannotValidateDatapoint("dp3")

    asyncio_run.side_effect = [accepted_dp, rejected_dp, cannot_dp]

    run_scheduled_processing()

    db_engine.add_entity.assert_called_once()
    inserted = db_engine.add_entity.call_args[0][0]

    assert inserted.data_id == "D123"
    assert inserted.review_completed is True

    msg = slack.send_slack_message.call_args[0][0]
    assert "Accepted: 1" in msg
    assert "Rejected: 1" in msg
    assert "Not validated: 1" in msg


@pytest.fixture(autouse=True)
def mock_db_setup() -> Iterator[None]:
    """Fixture to set up and tear down the database for testing."""
    with (
        patch("dataland_qa_lab.database.database_engine.create_tables"),
        patch("dataland_qa_lab.database.database_engine.verify_database_connection"),
    ):
        yield


@pytest.fixture
def server_mocks() -> Iterator[dict[str, Any]]:
    """Fixture to mock config and scheduler in server."""
    with (
        patch("dataland_qa_lab.bin.server.config") as config_mock,
        patch("dataland_qa_lab.bin.server.scheduler") as scheduler_mock,
        patch("dataland_qa_lab.bin.server.data_point_scheduler.run_scheduled_processing") as mock_job_func,
    ):
        yield {"app": app, "config": config_mock, "scheduler": scheduler_mock, "job_func": mock_job_func}
