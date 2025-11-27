# main.py
import json
import logging
import sys
import time
from collections import Counter

from qa_lab_monitor.qalab_api import check_qalab_api_health, review_data_point_on_qalab
from qa_lab_monitor.utils import load_config, store_output

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


analytics = Counter()


def monitor_data_points(data_points: list[str], ai_model: str, config) -> None:
    """Monitor data_points by comparing source of truth with QALab responses."""
    for data_point_id in data_points:
        logger.info("Processing document: %s", data_point_id)

        qalab_response = review_data_point_on_qalab(
            data_point_id=data_point_id, ai_model=ai_model, use_ocr=config.use_ocr
        )

        store_output(
            file_name=data_point_id,
            data=qalab_response,
            format_as_json=True,
        )

        analytics["total_fields"] += 1
        if qalab_response.get("qa_status") == "Accepted":
            analytics["qa_accepted"] += 1
        elif qalab_response.get("qa_status") == "Rejected":
            analytics["qa_rejected"] += 1
        elif qalab_response.get("qa_status") == "Pending":
            analytics["qa_pending"] += 1
        analytics["average_confidence"] += qalab_response.get("confidence", 0)


def main() -> None:
    """Main monitoring function."""
    config = load_config()

    logger.info("======= Starting Monitoring =======")
    logger.info("======= Please note this script currently only works for nuclear and gas datasets =======")

    start_time = int(time.time())

    if not config.data_points:
        logger.warning("No data points specified in config. Please add data point IDs to monitor.")
        sys.exit(1)

    logger.info("Using AI Model: %s", config.ai_model)

    logger.info("Checking QALab API health...")
    check_qalab_api_health()

    logger.info("Monitoring the following data points: %s", ", ".join(config.data_points))
    monitor_data_points(data_points=config.data_points, ai_model=config.ai_model, config=config)

    end_time = int(time.time())
    store_output(
        file_name="monitoring_summary",
        data={
            "total_fields": analytics["total_fields"],
            "qa_accepted": analytics["qa_accepted"],
            "qa_rejected": analytics["qa_rejected"],
            "qa_pending": analytics["qa_pending"],
            "average_confidence": analytics["average_confidence"] / analytics["total_fields"]
            if analytics["total_fields"] > 0
            else 0,
            "start_time": start_time,
            "end_time": end_time,
            "monitoring_duration_seconds": end_time - start_time,
            "score_percent": analytics["qa_accepted"] / analytics["total_fields"]
            if analytics["total_fields"] > 0
            else 0,
        },
        timestamp=False,
        format_as_json=True,
    )


if __name__ == "__main__":
    main()
