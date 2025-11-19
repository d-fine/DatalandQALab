import json
import logging

from dataland_backend.models.company_associated_data_nuclear_and_gas_data import (
    CompanyAssociatedDataNuclearAndGasData,
)

from dataland_qa_lab.categories.nuclear_and_gas_data.prompting import NuclearAndGasPrompting
from dataland_qa_lab.database.database_engine import add_entity

# import data providers
from dataland_qa_lab.database.database_tables import ReviewedDataset
from dataland_qa_lab.dataland.alerting import send_alert_message
from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.review.dataset_reviewer import update_reviewed_dataset_in_database
from dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator import NuclearAndGasReportGenerator
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.datetime_helper import get_german_time_as_string

logger = logging.getLogger(__name__)


def review_nuclear_and_gas_dataset(
    data_id: str, dataset: CompanyAssociatedDataNuclearAndGasData, force_override: bool = False
) -> str | None:
    """Execute the complete review process for a Nuclear and Gas dataset."""
    datetime_now = get_german_time_as_string()

    message = f"🔍 Starting review of the Dataset with the Data-ID: {data_id}"
    send_alert_message(message=message)

    review_dataset = ReviewedDataset(data_id=data_id, review_start_time=datetime_now)

    logger.info("Adding the dataset to the database.")
    add_entity(review_dataset)

    logger.info("Data collection created.")

    dataset_json = json.loads(dataset.json())

    promper = NuclearAndGasPrompting()

    for k, v in dataset_json.get("data").get("general").get("general").items():
        relevant_page = v.get("data_source").get("page")
        relevant_report = v.get("data_source").get("file_name")

        promper.run_prompt(k, "unknown")

    return dataset
    page_numbers = pages_provider.get_nuclear_and_gas_page_numbers(data_collection)
    relevant_pages_pdf_reader = pages_provider.get_relevant_pages_of_pdf(data_collection)

    if relevant_pages_pdf_reader is None:
        report = NuclearAndGasReportGenerator().generate_report(relevant_pages=None, dataset=data_collection)
    else:
        readable_text = text_to_doc_intelligence.get_markdown_from_dataset(
            data_id=data_id, page_numbers=page_numbers, relevant_pages_pdf_reader=relevant_pages_pdf_reader
        )

        report = NuclearAndGasReportGenerator().generate_report(relevant_pages=readable_text, dataset=data_collection)

    # force overriding the data in dataland.
    if force_override:
        data = config.get_config().dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report(
            data_id=data_id, nuclear_and_gas_data=report
        )
        logger.info("Report ID: %s", data.qa_report_id)

        update_reviewed_dataset_in_database(data_id=data_id, report_id=data.qa_report_id)

    send_alert_message(message=f"Review is complete for dataset with ID: {data_id}.")

    logger.info("Report posted successfully for dataset with ID: %s", data_id)
    return report
