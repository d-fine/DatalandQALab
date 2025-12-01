import logging
from collections import Counter

from dataland_qa.models.qa_status import QaStatus

from qa_lab.dataland import dataland_client
from qa_lab.utils import config, slack
from qa_lab.validator import validator

logger = logging.getLogger(__name__)
config = config.get_config()

dataland_client = dataland_client.DatalandClient(config.dataland_url, config.dataland_api_key)


def run_scheduled_processing() -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    logger.info("Scheduled processing started.")
    unreviewed_datasets = dataland_client.qa_api.get_info_on_datasets(
        qa_status=QaStatus.PENDING, chunk_size=2, data_types=["sfdr"]
    )

    logger.info("Found %d unreviewed datasets. Starting processing.", len(unreviewed_datasets))
    for dataset in unreviewed_datasets:
        slack.send_slack_message("------------------------------------------------------------------")
        slack.send_slack_message(f"⏳ Starting validation for dataset ID: {dataset.data_id}")
        logger.info("Processing dataset ID: %s", dataset.data_id)
        data_points = dataland_client.metadata_api.get_contained_data_points(dataset.data_id)

        qa_status = Counter()

        for k, v in data_points.items():
            slack.send_slack_message(f"--- ⏳ Starting validation for data point ID: {v} of kind {k}")
            logger.info("Validating of type %s data point ID: %s", k, v)
            try:
                validator_response = validator.validate_datapoint(
                    v, ai_model=config.ai_model, use_ocr=config.use_ocr, override=True
                )
                if validator_response.qa_status is QaStatus.ACCEPTED:
                    slack.send_slack_message(f"--- ✅ Data point ID: {v} accepted.")
                    logger.info("Data point ID: %s accepted.", v)
                else:
                    slack.send_slack_message(f"--- ❌ Data point ID: {v} rejected.")
                    logger.info("Data point ID: %s rejected.", v)
                qa_status[validator_response.qa_status] += 1
            except Exception as e:
                slack.send_slack_message(
                    f"--- 🟡 Error processing data point ID: {v}. Report stays in pending. With the following Error: {e!s}"  # noqa: E501
                )
                logger.exception("Error processing data point ID %s", v)
                qa_status[QaStatus.PENDING] += 1

        if qa_status[QaStatus.ACCEPTED] == len(data_points):
            logger.info("All data points accepted for dataset ID: %s", dataset.data_id)
            dataland_client.qa_api.change_qa_status(
                data_id=dataset.data_id, qa_status=QaStatus.ACCEPTED, overwrite_data_point_qa_status=False
            )
            slack.send_slack_message(f"🎉 Dataset ID: {dataset.data_id} accepted with all data points.")
        else:
            logger.info(
                "Dataset ID: %s has %d Accepted, %d Rejected data points. Marking as Rejected.",
                dataset.data_id,
                qa_status[QaStatus.ACCEPTED],
                qa_status[QaStatus.REJECTED],
            )

            dataland_client.qa_api.change_qa_status(
                data_id=dataset.data_id, qa_status=QaStatus.REJECTED, overwrite_data_point_qa_status=False
            )
            slack.send_slack_message(
                f"⚠️ Dataset ID: {dataset.data_id} rejected with "
                f"{qa_status[QaStatus.ACCEPTED]} accepted and {qa_status[QaStatus.REJECTED]} rejected data points."
            )
