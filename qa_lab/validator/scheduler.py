import logging
from collections import Counter

from qa_lab.dataland.api import QaStatus, get_dataset_data_points, get_pending_datasets, set_dataset_status
from qa_lab.utils.config import get_config
from qa_lab.utils.slack import send_slack_message
from qa_lab.validator.validator import validate_datapoint

logger = logging.getLogger(__name__)
conf = get_config()


def run_scheduled_processing() -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    logger.info("Scheduled processing started.")
    unreviewed_datasets = get_pending_datasets()

    send_slack_message("------------------------------------------------------------------")
    logger.info("Found %d unreviewed datasets. Starting processing.", len(unreviewed_datasets))
    for dataset in unreviewed_datasets:
        send_slack_message(f"⏳ Starting validation for dataset ID: {dataset.get('dataId', '')}")
        logger.info("Processing dataset ID: %s", dataset.get("dataId", ""))
        data_points = get_dataset_data_points(dataset_id=dataset.get("dataId", ""))

        qa_status = Counter()

        for k, v in data_points.items():
            send_slack_message(f"--- ⏳ Starting validation for data point ID: {v} of kind {k}")
            logger.info("Validating of type %s data point ID: %s", k, v)
            try:
                res = validate_datapoint(v, ai_model=conf.ai_model, use_ocr=conf.use_ocr, override=True)
                if res.get("qa_status") is QaStatus.Accepted:
                    send_slack_message(f"--- ✅ Data point ID: {v} accepted.")
                    logger.info("Data point ID: %s accepted.", v)
                else:
                    send_slack_message(f"--- ❌ Data point ID: {v} rejected.")
                    logger.info("Data point ID: %s rejected.", v)
                qa_status[res["qa_status"]] += 1
            except Exception as e:
                send_slack_message(
                    f"--- 🟡 Error processing data point ID: {v}. Report stays in pending. With the following Error: {e!s}"  # noqa: E501
                )
                logger.exception("Error processing data point ID %s", v)
                qa_status[QaStatus.Pending] += 1

        if qa_status["Accepted"] == len(data_points):
            logger.info("All data points accepted for dataset ID: %s", dataset.get("dataId", ""))
            set_dataset_status(dataset.get("dataId", ""), QaStatus.Accepted)
            send_slack_message(f"🎉 Dataset ID: {dataset.get('dataId', '')} accepted with all data points.")
        else:
            logger.info(
                "Dataset ID: %s has %d Accepted, %d Rejected data points. Marking as Rejected.",
                dataset.get("dataId", ""),
                qa_status["Accepted"],
                qa_status["Rejected"],
            )
            set_dataset_status(dataset.get("dataId", ""), QaStatus.Rejected)
            send_slack_message(
                f"⚠️ Dataset ID: {dataset.get('dataId', '')} rejected with "
                f"{qa_status['Accepted']} accepted and {qa_status['Rejected']} rejected data points."
            )
