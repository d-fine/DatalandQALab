import asyncio
import logging
from collections import Counter

from dataland_qa.models.qa_status import QaStatus

from dataland_qa_lab.data_point_flow import review
from dataland_qa_lab.utils import config, slack

logger = logging.getLogger(__name__)
config = config.get_config()


def run_scheduled_processing() -> None:
    """Continuously processes unreviewed datasets at scheduled intervals."""
    logger.info("Scheduled processing started.")
    slack_message = []
    unreviewed_datasets = config.dataland_client.qa_api.get_info_on_datasets(
        qa_status=QaStatus.PENDING, chunk_size=2, data_types=config.frameworks_list
    )

    logger.info("Found %d unreviewed datasets. Starting processing.", len(unreviewed_datasets))
    for dataset in unreviewed_datasets:
        slack_message.append(f"⏳ Starting validation for dataset ID: {dataset['data_id']}")
        logger.info("Processing dataset ID: %s", dataset["data_id"])
        data_points = config.dataland_client.meta_api.get_contained_data_points(dataset["data_id"])

        accepted_ids = []
        rejected_ids = []
        not_validated_ids = []

        for k, v in data_points.items():
            logger.info("Validating of type %s data point ID: %s", k, v)
            try:
                validator_response = asyncio.run(
                    review.validate_datapoint(
                        data_point_id=v,
                        ai_model=config.ai_model,
                        use_ocr=config.use_ocr,
                        override=False,
                    )
                )

                if isinstance(validator_response, review.models.ValidatedDatapoint):
                    if validator_response.qa_status == "Accepted":
                        logger.info("Data point ID: %s accepted.", v)
                        accepted_ids.append(v)
                    if validator_response.qa_status == "Rejected":
                        logger.info("Data point ID: %s rejected.", v)
                        rejected_ids.append(v)
                else:
                    not_validated_ids.append(v)

            except Exception:
                pass

        logger.info("All data points accepted for dataset ID: %s", dataset["data_id"])
        config.dataland_client.qa_api.change_qa_status(
            data_id=dataset["data_id"], qa_status=QaStatus.PENDING, overwrite_data_point_qa_status=False
        )

        slack_message.append(
            ":white_check_mark: Accepted " + str(len(accepted_ids)) + " ids:" + ", ".join(accepted_ids)
        )
        slack_message.append(":x: Rejected " + str(len(rejected_ids)) + " ids:" + ", ".join(rejected_ids))
        slack_message.append(
            ":warning: Not validated " + str(len(not_validated_ids)) + " ids:" + ", ".join(not_validated_ids)
        )

        slack.send_slack_message("\n".join(slack_message))
