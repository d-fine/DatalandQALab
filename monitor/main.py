import json
import logging
import sys

from monitor.qalab_api import check_qalab_api_health, run_report_on_qalab
from monitor.utils import load_config, store_output
from src.dataland_qa_lab.dataland.dataset_provider import get_dataset_by_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
config = load_config()


def monitor_documents(documents: list[str], ai_model: str) -> None:
    """Monitor documents by comparing source of truth with QALab responses."""
    for document_id in documents:
        logger.info("Processing document: %s", document_id)
        dataland_response = get_dataset_by_id(document_id)

        if not dataland_response:
            logger.warning("Failed to retrieve dataset for document ID: %s", document_id)
            continue

        # Convert dataset to Python dict
        try:
            source_of_truth = json.loads(dataland_response.model_dump_json())
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse dataset for document ID: %s: %s", document_id, e)
            continue

        qalab_response = run_report_on_qalab(data_id=document_id, ai_model=ai_model, use_ocr=False)  # noqa: F841
        store_output(source_of_truth, "test", format_as_json=True)


def main() -> None:
    """Main monitoring function."""
    # todo: change this!!!
    logger.info("======= Starting Monitoring =======")
    logger.info("======= Please note this script currently only works for nuclear and gas datasets =======")

    # setting defaults, not sure if this is ideal or exiting would be better

    if not config.documents:
        logger.warning("No documents specified in config. Please add document IDs to monitor.")
        sys.exit(1)

    logger.info("Using AI Model: %s", config.ai_model)

    logger.info("Checking QALab API health...")
    check_qalab_api_health()

    logger.info("Monitoring the following documents: %s", ", ".join(config.documents))
    monitor_documents(documents=config.documents, ai_model=config.ai_model)


if __name__ == "__main__":
    main()
