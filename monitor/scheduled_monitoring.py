import json
import logging
import time
from collections.abc import Iterable
from dataclasses import dataclass

from utils import db, qalab

logger = logging.getLogger(__name__)
POLL_INTERVAL_SECONDS = 5


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration for an experiment run."""

    experiment_id: int
    experiment_type: str
    ids: list[str]
    model: str
    use_ocr: bool
    override: bool
    qalab_base_url: str


def _process_result(
    experiment_id: int,
    data_id: str,
    ids: list[str],
    result: dict,
) -> list[str]:
    db.create_result(experiment_id, data_id, json.dumps(result))
    remaining = [item for item in ids if item != data_id]
    db.update_experiment(experiment_id, ids=json.dumps(remaining))
    return remaining


def _build_error_payload(error: Exception, experiment_type: str) -> dict:
    if experiment_type == "dataset":
        return {
            "error": {
                "qa_status": "MonitorError",
                "message": "Error Monitor could not process the request.",
                "error": str(error),
            }
        }
    return {
        "qa_status": "MonitorError",
        "message": "Error Monitor could not process the request.",
        "error": str(error),
    }


def _run_request(config: ExperimentConfig, data_id: str) -> dict:
    if config.experiment_type == "dataset":
        return qalab.review_dataset(
            qalab_base_url=config.qalab_base_url,
            dataset_id=data_id,
            ai_model=config.model,
            use_ocr=config.use_ocr,
            override=config.override,
        )
    return qalab.review_data_point(
        qalab_base_url=config.qalab_base_url,
        data_point_id=data_id,
        ai_model=config.model,
        use_ocr=config.use_ocr,
        override=config.override,
    )


def _process_pending_ids(config: ExperimentConfig, ids: Iterable[str]) -> None:
    remaining_ids = list(ids)
    for data_id in list(remaining_ids):
        logger.info(
            "Processing %s ID: %s with model %s, override=%s and use_ocr=%s",
            config.experiment_type,
            data_id,
            config.model,
            config.override,
            config.use_ocr,
        )

        try:
            result = _run_request(config, data_id)
        except Exception as error:
            logger.exception("Monitor error for %s ID %s", config.experiment_type, data_id)
            remaining_ids = _process_result(
                config.experiment_id,
                data_id,
                remaining_ids,
                _build_error_payload(error, config.experiment_type),
            )
        else:
            remaining_ids = _process_result(
                config.experiment_id,
                data_id,
                remaining_ids,
                result,
            )


def check() -> None:
    """Run experiments if any are pending."""
    experiment = db.get_latest_experiment()
    if not experiment:
        return

    experiment_id, experiment_type, ids, model, use_ocr, override, qalab_base_url, _timestamp = experiment
    json_ids = json.loads(ids)
    config = ExperimentConfig(
        experiment_id=experiment_id,
        experiment_type=experiment_type,
        ids=json_ids,
        model=model,
        use_ocr=bool(use_ocr),
        override=bool(override),
        qalab_base_url=qalab_base_url,
    )
    _process_pending_ids(config, json_ids)


def main() -> None:
    """Run the scheduled monitoring loop."""
    logging.basicConfig(level=logging.INFO)
    while True:
        check()
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
