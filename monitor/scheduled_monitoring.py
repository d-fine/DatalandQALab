import json
import logging
import time

from utils import db, qalab

logger = logging.getLogger()


def check() -> None:
    """Run experiments if any are pending."""
    experiment = db.get_latest_experiment()
    if experiment:
        experiment_id, experiment_type, ids, model, use_ocr, override, qalab_base_url, _timestamp = experiment
        json_ids = json.loads(ids)
        for data_id in json_ids:
            logger.info(
                "Processing %s ID: %s with model %s, override=%s and use_ocr=%s",
                experiment_type,
                data_id,
                model,
                override,
                use_ocr,
            )

            try:
                if experiment_type == "dataset":
                    result = qalab.review_dataset(
                        qalab_base_url=qalab_base_url,
                        dataset_id=data_id,
                        ai_model=model,
                        use_ocr=bool(use_ocr),
                        override=override,
                    )
                else:
                    result = qalab.review_data_point(
                        qalab_base_url=qalab_base_url,
                        data_point_id=data_id,
                        ai_model=model,
                        use_ocr=bool(use_ocr),
                        override=override,
                    )
                new_ids = json_ids.copy()
                new_ids.remove(data_id)
                db.update_experiment(experiment_id, ids=json.dumps(new_ids))
                json_ids = new_ids

                db.create_result(experiment_id, data_id, json.dumps(result))

            except Exception as e:  # noqa: BLE001
                new_ids = json_ids.copy()
                new_ids.remove(data_id)
                db.update_experiment(experiment_id, ids=json.dumps(new_ids))
                json_ids = new_ids
                if experiment_type == "dataset":
                    db.create_result(
                        experiment_id,
                        data_id,
                        json.dumps(
                            {
                                "error": {
                                    "qa_status": "MonitorError",
                                    "message": "Error Monitor could not process the request.",
                                    "error": str(e),
                                }
                            }
                        ),
                    )
                else:
                    db.create_result(
                        experiment_id,
                        data_id,
                        json.dumps(
                            {
                                "qa_status": "MonitorError",
                                "message": "Error Monitor could not process the request.",
                                "error": str(e),
                            }
                        ),
                    )


while True:
    check()
    time.sleep(5)  # Check every 5 seconds
