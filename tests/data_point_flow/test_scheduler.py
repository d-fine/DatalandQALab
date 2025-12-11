from unittest.mock import MagicMock, patch

import pytest
from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow.scheduler import run_scheduled_processing


@pytest.fixture
def mock_config():  # noqa: ANN201
    with patch("dataland_qa_lab.data_point_flow.scheduler.config") as cfg:
        cfg.dataland_client.qa_api.get_number_of_pending_datasets.return_value = 2
        cfg.dataland_client.qa_api.get_info_on_datasets.return_value = [
            MagicMock(data_id="D1"),
        ]
        cfg.dataland_client.meta_api.get_contained_data_points.return_value = {
            "a": "DP_A",
            "b": "DP_B",
        }

        cfg.ai_model = "mockmodel"
        cfg.use_ocr = False

        yield cfg


@pytest.fixture
def mock_db():  # noqa: ANN201
    """Fixture to mock the database_engine module in the scheduler."""
    with patch("dataland_qa_lab.data_point_flow.scheduler.database_engine") as db:
        db.get_entity.return_value = None
        yield db


@pytest.fixture
def mock_tables():  # noqa: ANN201
    """Fixture to mock the database_tables module in the scheduler."""
    with patch("dataland_qa_lab.data_point_flow.scheduler.database_tables") as tbl:
        tbl.ReviewedDataset = MagicMock()
        yield tbl


@pytest.fixture
def mock_slack():  # noqa: ANN201
    """Fixture to mock the slack module in the scheduler."""
    with patch("dataland_qa_lab.data_point_flow.scheduler.slack") as s:
        yield s


@pytest.fixture
def mock_review_validation() -> None:
    """Fixture to mock the validate_datapoint function in the review module."""
    with patch("dataland_qa_lab.data_point_flow.scheduler.review.validate_datapoint") as validate:

        class MockValidated:
            def __init__(self, data_point_id: str, qa_status: QaStatus) -> None:
                """Test ValidatedDatapoint mock."""
                self.data_point_id = data_point_id
                self.qa_status = qa_status

        class MockCannotValidate:
            def __init__(self, data_point_id: str) -> None:
                """Test CannotValidateDatapoint mock."""
                self.data_point_id = data_point_id

        def side_effect(
            data_point_id: str,
            ai_model: str,  # noqa: ARG001
            use_ocr: str,  # noqa: ARG001
            override: bool,  # noqa: ARG001
        ) -> MockValidated | MockCannotValidate:
            """Test side effect function for validate_datapoint mock."""
            if data_point_id == "DP_A":
                return MockValidated("DP_A", QaStatus.ACCEPTED)

            return MockCannotValidate("DP_B")

        validate.side_effect = side_effect

        validate.models = MagicMock()
        validate.models.ValidatedDatapoint = MockValidated
        validate.models.CannotValidateDatapoint = MockCannotValidate

        yield validate


def test_run_scheduled_processing(
    mock_config: MagicMock,  # noqa: ARG001
    mock_db: MagicMock,
    mock_tables: MagicMock,  # noqa: ARG001
    mock_slack: MagicMock,
    mock_review_validation: MagicMock,
) -> None:
    """Test run_scheduled_processing processes datasets and sends Slack messages."""
    run_scheduled_processing()

    assert mock_db.add_entity.called

    msg = mock_slack.send_slack_message.call_args[0][0]
    assert "Accepted: 0" in msg
    assert "Not validated: 0" in msg

    assert mock_review_validation.call_count == 2
