import logging

from dataland_qa_lab.database.database_engine import add_entity, delete_entity, get_entity, update_entity
from dataland_qa_lab.database.database_tables import ReviewedDataset
from dataland_qa_lab.dataland import dataset_provider
from dataland_qa_lab.dataland.alerting import send_alert_message
from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator import NuclearAndGasReportGenerator
from dataland_qa_lab.review.report_generator.sfdr_report_generator import SfdrReportGenerator
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.datetime_helper import get_german_time_as_string
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection
from dataland_qa_lab.utils.sfdr_data_collection import SFDRDataCollection

logger = logging.getLogger(__name__)


def review_dataset(data_id: str, framework: str = "sfdr", force_review: bool = False) -> str | None:
    """Review dataset based on its framework."""
    logger.info("Starting the review of the Dataset: %s (Framework: %s)", data_id, framework)

    existing_report = get_entity(data_id, ReviewedDataset)

    if existing_report is not None and existing_report.report_id is None:
        logger.warning("Found incomplete/stale review for %s. Cleaning up to restart.", data_id)
        delete_entity(data_id, ReviewedDataset)
        existing_report = None

    if force_review and existing_report is not None:
        logger.info("Deleting old review from the database")
        delete_entity(data_id, ReviewedDataset)
        existing_report = None

    if existing_report is None:
        logger.info("Dataset with the Data-ID does not exist in the database. Starting review.")

        if framework == "nuclear-and-gas":
            return review_nuclear_and_gas_dataset(data_id)

        if framework == "sfdr":
            return review_sfdr_dataset(data_id)

        logger.error("Unknown framework: %s for Data-ID: %s", framework, data_id)
        return None

    logger.info("Report for data_id already exists.")
    return existing_report.report_id


def review_nuclear_and_gas_dataset(data_id: str) -> str | None:
    """Execute the complete review process for a Nuclear and Gas dataset."""
    dataset = dataset_provider.get_dataset_by_id(data_id)
    datetime_now = get_german_time_as_string()

    message = f"🔍 Starting review of the Dataset with the Data-ID: {data_id}"
    send_alert_message(message=message)

    review_dataset_entry = ReviewedDataset(data_id=data_id, review_start_time=datetime_now)

    logger.info("Adding the dataset to the database.")
    add_entity(review_dataset_entry)

    data_collection = NuclearAndGasDataCollection(dataset.data)
    logger.info("Data collection created.")

    page_numbers = pages_provider.get_relevant_page_numbers(data_collection)
    relevant_pages_pdf_reader = pages_provider.get_relevant_pages_of_pdf(data_collection)

    if relevant_pages_pdf_reader is None:
        report = NuclearAndGasReportGenerator().generate_report(relevant_pages=None, dataset=data_collection)
    else:
        readable_text = text_to_doc_intelligence.get_markdown_from_dataset(
            data_id=data_id, page_numbers=page_numbers, relevant_pages_pdf_reader=relevant_pages_pdf_reader
        )

        report = NuclearAndGasReportGenerator().generate_report(relevant_pages=readable_text, dataset=data_collection)

    data = config.get_config().dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report(
        data_id=data_id, nuclear_and_gas_data=report
    )

    update_reviewed_dataset_in_database(data_id=data_id, report_id=data.qa_report_id)

    message = f"✅ Review is successful for the dataset with the Data-ID: {data_id}. Report ID: {data.qa_report_id}"
    send_alert_message(message=message)

    logger.info("Report posted successfully for dataset with ID: %s", data_id)
    logger.info("Report ID: %s", data.qa_report_id)
    return data.qa_report_id


def review_sfdr_dataset(data_id: str) -> str | None:
    """Execute the complete review process for a SFDR dataset."""
    dataset = dataset_provider.get_sfdr_dataset_by_id(data_id)
    datetime_now = get_german_time_as_string()

    message = f"🔍 Starting review of the Dataset with the Data-ID: {data_id}"
    send_alert_message(message=message)

    review_dataset_entry = ReviewedDataset(data_id=data_id, review_start_time=datetime_now)

    logger.info("Adding the dataset to the database.")
    add_entity(review_dataset_entry)

    data_collection = SFDRDataCollection(dataset.data)
    logger.info("Data collection created.")

    try:
        page_numbers = pages_provider.get_sfdr_page_numbers(data_collection)
    except AttributeError:
        page_numbers = pages_provider.get_relevant_page_numbers(data_collection)

    relevant_pages_pdf_reader = pages_provider.get_relevant_pages_of_pdf(data_collection)

    if relevant_pages_pdf_reader is None:
        report = SfdrReportGenerator().generate_report(relevant_pages=None, dataset=data_collection)
    else:
        readable_text = text_to_doc_intelligence.get_markdown_from_dataset(
            data_id=data_id, page_numbers=page_numbers, relevant_pages_pdf_reader=relevant_pages_pdf_reader
        )

        report = SfdrReportGenerator().generate_report(relevant_pages=readable_text, dataset=data_collection)

    data = config.get_config().dataland_client.sfdr_qa_api.post_sfdr_data_qa_report(data_id=data_id, sfdr_data=report)

    update_reviewed_dataset_in_database(data_id=data_id, report_id=data.qa_report_id)

    message = f"✅ Review is successful for the dataset with the Data-ID: {data_id}. Report ID: {data.qa_report_id}"
    send_alert_message(message=message)

    logger.info("Report posted successfully for dataset with ID: %s", data_id)
    logger.info("Report ID: %s", data.qa_report_id)
    return data.qa_report_id


def update_reviewed_dataset_in_database(data_id: str, report_id: str) -> None:
    """After review set the database entry to finished and add review end time."""
    datetime_now = get_german_time_as_string()

    review_dataset_entry = ReviewedDataset(
        data_id=data_id, review_end_time=datetime_now, report_id=report_id, review_completed=True
    )

    update_entity(review_dataset_entry)
