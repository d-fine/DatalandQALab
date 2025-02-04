import logging

from dataland_qa.models.qa_report_meta_information import QaReportMetaInformation

from dataland_qa_lab.database.database_engine import add_entity, get_entity, update_entity
from dataland_qa_lab.database.database_tables import ReviewedDataset
from dataland_qa_lab.dataland import dataset_provider
from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator import NuclearAndGasReportGenerator
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.datetime import get_german_time_as_string
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection

logger = logging.getLogger(__name__)


def review_dataset(data_id: str, force_review: bool = False) -> QaReportMetaInformation | None:
    """Review a dataset."""
    logger.info("Starting the review of the Dataset: %s", data_id)

    dataset = dataset_provider.get_dataset_by_id(data_id)

    existing_entity = None if force_review else get_entity(data_id, ReviewedDataset)

    logger.info("Checking if the dataset is already existing in the database")
    if existing_entity is None:
        datetime_now = get_german_time_as_string()

        logger.info("Dataset with the Data-ID does not exist in the database. Starting review.")
        review_dataset = ReviewedDataset(data_id=data_id, review_start_time=datetime_now)

        logger.info("Adding the dataset in the database with the Data-ID and review start time.")
        add_entity(review_dataset)

        data_collection = NuclearAndGasDataCollection(dataset.data)
        logger.info("Data collection created.")

        page_numbers = pages_provider.get_relevant_page_numbers(data_collection)
        logger.info("Relevant page numbers extracted.")

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

        datetime_now = get_german_time_as_string()

        logger.debug("Adding review end time in the database.")
        review_dataset.review_end_time = datetime_now

        logger.debug("Adding review completed to the database.")
        review_dataset.review_completed = True

        logger.debug("Adding the Report-ID to the database.")
        review_dataset.report_id = data.qa_report_id

        update_entity(review_dataset)

        logger.info("Report posted successfully for dataset with ID: %s", data_id)
        return data
    logger.info("Dataset with the Data-ID already exist in the database.")
    return None
