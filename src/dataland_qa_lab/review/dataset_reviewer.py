import logging

from dataland_qa.models.qa_report_meta_information import QaReportMetaInformation

from dataland_qa_lab.dataland import dataset_provider
from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator import NuclearAndGasReportGenerator
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def review_dataset(data_id: str) -> QaReportMetaInformation | None:
    """Review a dataset."""
    try:
        # Fetch the dataset
        dataset = dataset_provider.get_dataset_by_id(data_id)
        if dataset is None:
            logging.exception("Dataset with ID %s not found.", data_id)
        # Create a data collection
        data_collection = NuclearAndGasDataCollection(dataset.data)
        if not data_collection:
            logging.exception("Data collection for dataset ID %s is invalid.", data_id)
        # Extract relevant pages and text
        relevant_pages_pdf_reader = pages_provider.get_relevant_pages_of_pdf(data_collection)
        if not relevant_pages_pdf_reader:
            logging.exception("Failed to extract relevant pages for dataset ID %s.", data_id)
        # Extract text from the relevant pages
        readable_text = text_to_doc_intelligence.extract_text_of_pdf(relevant_pages_pdf_reader)
        if not readable_text:
            logging.exception("No readable text extracted for dataset ID %s.", data_id)
        # Generate report
        report = NuclearAndGasReportGenerator().generate_report(relevant_pages=readable_text, dataset=data_collection)
        if not report:
            logging.exception("Failed to generate report for dataset ID %s.", data_id)

        config.get_config().dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report(
            data_id=data_id, nuclear_and_gas_data=report
        )
        logging.info("Successfully reviewed dataset %s.", data_id)
    except Exception as e:
        msg = f"Error reviewing dataset {data_id}: {e}"
        raise RuntimeError(msg) from e
