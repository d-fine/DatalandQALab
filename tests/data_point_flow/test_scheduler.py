from __future__ import annotations

import time
from dataclasses import dataclass
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from dataland_qa_lab.bin.server import app as dataland_qa_lab
from dataland_qa_lab.data_point_flow.scheduler import (
    lock_ttl_seconds,
    run_scheduled_processing,
    try_acquire_lock,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


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
            self,
            data_id: str,
            review_start_time: int,
            review_end_time: int,
            review_completed: bool,
            report_id: str | None,
        ) -> None:
            """Initialize ReviewedDataset."""
            self.data_id = data_id
            self.review_start_time = review_start_time
            self.review_end_time = review_end_time
            self.review_completed = review_completed
            self.report_id = report_id

    class DatapointInReview:
        def __init__(self, data_point_id: str) -> None:
            """Initialize DatapointInReview."""
            self.data_point_id = data_point_id

    db_tables.ReviewedDataset = ReviewedDataset
    db_tables.DatapointInReview = DatapointInReview

    dataset = MagicMock()
    dataset.data_id = "D123"
    config.dataland_client.qa_api.get_number_of_pending_datasets.return_value = 1
    config.dataland_client.qa_api.get_info_on_datasets.return_value = [dataset]

    db_engine.get_entity.return_value = False
    db_engine.acquire_or_refresh_datapoint_lock.return_value = True

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

    assert db_engine.get_entity.call_count == 4
    assert db_engine.acquire_or_refresh_datapoint_lock.call_count == 3
    assert db_engine.add_entity.call_count == 1
    assert db_engine.delete_entity.call_count == 3

    inserted_entities = [c.args[0] for c in db_engine.add_entity.call_args_list]
    inserted_reviewed = next(e for e in inserted_entities if isinstance(e, ReviewedDataset))

    assert inserted_reviewed.data_id == "D123"
    assert inserted_reviewed.review_completed is True

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
        patch("dataland_qa_lab.bin.server.conf", new=SimpleNamespace(
            is_local_environment=False,
            is_dev_environment=True)
        ),
        patch("dataland_qa_lab.bin.server.scheduler") as scheduler_mock,
        patch("dataland_qa_lab.bin.server.scheduled_job.run_scheduled_processing_job") as mock_job_func,
    ):
        yield {"app": dataland_qa_lab, "config": config_mock, "scheduler": scheduler_mock, "job_func": mock_job_func}


def test_scheduler_registers_wrapper_job(server_mocks: dict[str, Any]) -> None:
    """Test that the server registers the scheduled processing wrapper job on startup."""
    mocks = server_mocks
    with TestClient(mocks["app"]):
        pass

    scheduler_mock = mocks["scheduler"]
    assert scheduler_mock.add_job.called

    passed_function = scheduler_mock.add_job.call_args[0][0]
    assert passed_function == mocks["job_func"]


def test_try_acquire_no_existing(mocks: MagicMock) -> None:
    """Test acquiring lock when no existing lock."""
    db_engine = mocks["db_engine"]

    db_engine.get_entity.return_value = None
    db_engine.acquire_or_refresh_datapoint_lock.return_value = True

    assert try_acquire_lock("dp1") is True
    db_engine.acquire_or_refresh_datapoint_lock.assert_called_once_with(
        data_point_id="dp1",
        lock_ttl_seconds=lock_ttl_seconds,
    )
    db_engine.add_entity.assert_not_called()
    db_engine.delete_entity.assert_not_called()


def test_try_acquire_lock_existing_not_stale(mocks: MagicMock) -> None:
    """Test acquiring lock when existing lock."""
    db_engine = mocks["db_engine"]

    lock = MagicMock()
    lock.locked_at = int(time.time())
    db_engine.get_entity.return_value = lock

    assert try_acquire_lock("dp1") is False
    db_engine.acquire_or_refresh_datapoint_lock.assert_not_called()
    db_engine.add_entity.assert_not_called()
    db_engine.delete_entity.assert_not_called()


def test_try_acquire_lock_existing_stale(mocks: MagicMock) -> None:
    """Test acquiring lock when existing stale lock."""
    db_engine = mocks["db_engine"]

    lock = MagicMock()
    lock.locked_at = int(time.time()) - (lock_ttl_seconds + 1)
    db_engine.get_entity.return_value = lock

    db_engine.acquire_or_refresh_datapoint_lock.return_value = True

    assert try_acquire_lock("dp1") is True
    db_engine.acquire_or_refresh_datapoint_lock.assert_called_once_with(
        data_point_id="dp1",
        lock_ttl_seconds=lock_ttl_seconds,
    )
    db_engine.delete_entity.assert_not_called()
    db_engine.add_entity.assert_not_called()


def test_try_acquire_lock_not_acquired(mocks: MagicMock) -> None:
    """Test that lock acquisition returns False when lock cannot be acquired."""
    db_engine = mocks["db_engine"]

    db_engine.get_entity.return_value = None
    db_engine.acquire_or_refresh_datapoint_lock.return_value = False

    assert try_acquire_lock("dp1") is False
    db_engine.acquire_or_refresh_datapoint_lock.assert_called_once_with(
        data_point_id="dp1",
        lock_ttl_seconds=lock_ttl_seconds,
    )
    db_engine.add_entity.assert_not_called()
    db_engine.delete_entity.assert_not_called()


def test_process_dataset_continues_on_datapoint_exception(mocks: MagicMock) -> None:
    config = mocks["config"]
    review = mocks["review"]
    slack = mocks["slack"]
    db_engine = mocks["db_engine"]
    asyncio_run = mocks["asyncio_run"]
    logger = mocks["logger"]

    @dataclass
    class ValidatedDatapoint:
        data_point_id: str
        qa_status: str

    @dataclass
    class CannotValidateDatapoint:
        data_point_id: str

    review.models.ValidatedDatapoint = ValidatedDatapoint
    review.models.CannotValidateDatapoint = CannotValidateDatapoint

    dataset = MagicMock()
    dataset.data_id = "D123"
    config.dataland_client.qa_api.get_number_of_pending_datasets.return_value = 1
    config.dataland_client.qa_api.get_info_on_datasets.return_value = [dataset]

    db_engine.get_entity.return_value = False
    db_engine.acquire_or_refresh_datapoint_lock.return_value = True

    config.dataland_client.meta_api.get_contained_data_points.return_value = {
        "k1": "dp1",
        "k2": "dp2",
    }

    asyncio_run.side_effect = [
        Exception("boom"),
        ValidatedDatapoint("dp2", "QaAccepted"),
    ]

    run_scheduled_processing()

    assert asyncio_run.call_count == 2

    assert logger.exception.called

    assert db_engine.delete_entity.call_count == 2

    msg = slack.send_slack_message.call_args[0][0]
    assert "Accepted: 1" in msg
    assert "Not validated: 1" in msg


def test_process_dataset_continues_on_datapoint_timeout(mocks: MagicMock) -> None:
    config = mocks["config"]
    review = mocks["review"]
    slack = mocks["slack"]
    db_engine = mocks["db_engine"]
    asyncio_run = mocks["asyncio_run"]
    logger = mocks["logger"]

    @dataclass
    class ValidatedDatapoint:
        data_point_id: str
        qa_status: str

    review.models.ValidatedDatapoint = ValidatedDatapoint

    dataset = MagicMock()
    dataset.data_id = "D123"
    config.dataland_client.qa_api.get_number_of_pending_datasets.return_value = 1
    config.dataland_client.qa_api.get_info_on_datasets.return_value = [dataset]

    db_engine.get_entity.return_value = False
    db_engine.acquire_or_refresh_datapoint_lock.return_value = True

    config.dataland_client.meta_api.get_contained_data_points.return_value = {
        "k1": "dp1",
        "k2": "dp2",
    }

    asyncio_run.side_effect = [
        TimeoutError(),
        ValidatedDatapoint("dp2", "QaAccepted"),
    ]

    run_scheduled_processing()

    assert asyncio_run.call_count == 2
    assert db_engine.delete_entity.call_count == 2

    assert logger.warning.called

    msg = slack.send_slack_message.call_args[0][0]
    assert "Accepted: 1" in msg
    assert "Not validated: 1" in msg
