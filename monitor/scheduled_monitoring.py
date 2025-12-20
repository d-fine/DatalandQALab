import json
import time

from utils import db, qalab


def check() -> None:
    """Run experiments if any are pending."""
    experiment = db.get_latest_experiment()
    if experiment:
        id, type, ids, model, use_ocr, timestamp = experiment
        json_ids = json.loads(ids)
        for data_id in json_ids:
            print(f"Processing {type} ID: {data_id} with model {model} and use_ocr={use_ocr}")

            if type == "dataset":
                result = qalab.review_dataset(data_id, model, bool(use_ocr))
            else:
                result = qalab.review_data_point(data_id, model, bool(use_ocr))

            new_ids = json_ids.copy()
            new_ids.remove(data_id)
            db.update_experiment(id, ids=json.dumps(new_ids))
            json_ids = new_ids

            db.create_result(id, data_id, json.dumps(result))


while True:
    check()
    time.sleep(5)  # Check every 5 seconds
