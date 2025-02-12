import logging
from datetime import UTC, datetime, timedelta, timezone

from dataland_qa.models.qa_report_meta_information import QaReportMetaInformation

from dataland_qa_lab.database.database_engine import add_entity, get_entity, update_entity
from dataland_qa_lab.database.database_tables import ReviewedDataset
from dataland_qa_lab.dataland import dataset_provider
from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator import NuclearAndGasReportGenerator
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection

logger = logging.getLogger(__name__)


def review_dataset(data_id: str, single_pass_e2e: bool = False) -> QaReportMetaInformation | None:
    """Review a dataset."""
    logger.info("Starting the review of the Dataset: %s", data_id)

    dataset = dataset_provider.get_dataset_by_id(data_id)
    logger.debug("Dataset retrieved form the given Data-ID.")

    existing_entity = None if single_pass_e2e else get_entity(data_id, ReviewedDataset)

    now_utc = datetime.now(UTC)
    ger_timezone = timedelta(hours=2) if now_utc.astimezone(timezone(timedelta(hours=1))).dst() else timedelta(hours=1)
    formatted_german_time1 = (now_utc + ger_timezone).strftime("%Y-%m-%d %H:%M:%S")

    logger.debug("Checking if the dataset is already existing in the database")
    if existing_entity is None:
        logger.info("Dataset with the Data-ID does not exist in the database. Starting review.")
        review_dataset = ReviewedDataset(data_id=data_id, review_start_time=formatted_german_time1)

        logger.debug("Adding the dataset in the database with the Data-ID and review start time.")
        add_entity(review_dataset)

        data_collection = NuclearAndGasDataCollection(dataset.data)
        logger.debug("Data collection created.")

        page_numbers = pages_provider.get_relevant_page_numbers(data_collection)
        logger.debug("Relevant page numbers extracted.")

        relevant_pages_pdf_reader = pages_provider.get_relevant_pages_of_pdf(data_collection)
        if relevant_pages_pdf_reader is None:
            logger.debug("No Data source found for the relevant pages.")
            report = NuclearAndGasReportGenerator().generate_report(relevant_pages=None, dataset=data_collection)
            logger.info("QA not attempted report generated successfully.")

        else:
            logger.debug("Relevant pages extracted.")
            readable_text = text_to_doc_intelligence.get_markdown_from_dataset(
                data_id=data_id, page_numbers=page_numbers, relevant_pages_pdf_reader=relevant_pages_pdf_reader
            )
            logger.debug("Text extracted from the relevant pages.")

            report = NuclearAndGasReportGenerator().generate_report(
                relevant_pages=readable_text, dataset=data_collection
            )
            logger.info("Report generated succesfully.")

        data = config.get_config().dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report(
            data_id=data_id, nuclear_and_gas_data=report
        )

        now_utc = datetime.now(UTC)
        if now_utc.astimezone(timezone(timedelta(hours=1))).dst():
            ger_timezone = timedelta(hours=2)
        else:
            ger_timezone = timedelta(hours=1)

        formatted_german_time2 = (now_utc + ger_timezone).strftime("%Y-%m-%d %H:%M:%S")

        logger.debug("Adding review end time in the database.")
        review_dataset.review_end_time = formatted_german_time2

        logger.debug("Adding review completed to the database.")
        review_dataset.review_completed = True

        logger.debug("Adding the Report-ID to the database.")
        review_dataset.report_id = data.qa_report_id

        update_entity(review_dataset)

        logger.info("Report posted successfully for dataset with ID: %s", data_id)
        return data
    return None
