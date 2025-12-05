import json
import logging
import sys
import time
from collections import Counter

from monitor.categories import detect_category_from_dataset
from monitor.esg_monitor import ESGMonitor
from monitor.qalab_api import check_qalab_api_health, run_report_on_qalab
from monitor.utils import load_config, match_sot_and_qareport, store_output
from src.dataland_qa_lab.dataland.dataset_provider import get_dataset_by_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
config = load_config()

counter = Counter()


def monitor_documents(documents: list[str], ai_model: str) -> None:
    """Monitor documents by comparing source of truth with QALab responses.

    Now supports multiple ESG categories via detect_category_from_dataset and ESGMonitor.
    """
    for document_id in documents:
        logger.info("Processing document: %s", document_id)
        dataland_response = get_dataset_by_id(document_id)

        if not dataland_response:
            logger.warning("Failed to retrieve dataset for document ID: %s", document_id)
            continue

        try:
            source_of_truth = json.loads(dataland_response.model_dump_json())
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse dataset for document ID: %s: %s", document_id, e)
            continue

        # Detect category and validate using ESGMonitor
        category = detect_category_from_dataset(source_of_truth)
        if category:
            logger.info("Detected category for document %s: %s", document_id, category.value)
            monitor = ESGMonitor(category)
            validation_errors = monitor.validate(source_of_truth.get("data", {}).get("general", {}).get("general", {}))
            if validation_errors:
                logger.warning("Validation errors for document %s: %s", document_id, validation_errors)

        qalab_response = run_report_on_qalab(data_id=document_id, ai_model=ai_model, use_ocr=config.use_ocr)

        store_output(
            {
                "source_of_truth": source_of_truth,
                "qalab_response": qalab_response,
            },
            document_id,
            format_as_json=True,
        )

        logger.info("Starting matching for document ID: %s", document_id)
        # Pass category to match function for category-specific epsilon
        res = match_sot_and_qareport(
            source_of_truth=source_of_truth,
            qalab_report=qalab_response,
            category=category.value if category else None,
        )
        counter.update(res)

        # Track category statistics
        if category:
            counter[f"category_{category.value}"] += 1


def main() -> None:
    """Main monitoring function.

    Now supports multiple ESG categories including nuclear, gas, renewable energy, etc.
    """
    logger.info("======= Starting Monitoring =======")
    logger.info("======= Monitoring ESG datasets across multiple categories =======")

    start_time = int(time.time())

    if not config.documents:
        logger.warning("No documents specified in config. Please add document IDs to monitor.")
        sys.exit(1)

    logger.info("Using AI Model: %s", config.ai_model)

    logger.info("Checking QALab API health...")
    check_qalab_api_health()

    logger.info("Monitoring the following documents: %s", ", ".join(config.documents))
    monitor_documents(documents=config.documents, ai_model=config.ai_model)

    end_time = int(time.time())

    # Calculate category statistics
    category_stats = {}
    for key in counter:
        if key.startswith("category_"):
            category_stats[key.replace("category_", "")] = counter[key]

    store_output(
        {
            "total_fields_checked": counter["total_fields"],
            "total_documents_monitored": len(config.documents),
            "total_matches": counter["matches_count"],
            "total_mismatches": counter["mismatches_count"],
            "total_skipped": counter["skipped_count"],
            "start_time": start_time,
            "end_time": end_time,
            "monitoring_duration_seconds": end_time - start_time,
            "score_percent": counter["matches_count"] / counter["total_fields"] if counter["total_fields"] > 0 else 0,
        },
        "monitoring_summary",
        timestamp=False,
        format_as_json=True,
    )


if __name__ == "__main__":
    main()
