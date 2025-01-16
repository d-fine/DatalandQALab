from datetime import datetime

from dataland_qa_lab.database.database_engine import add_entity, get_entity, update_entity
from dataland_qa_lab.database.database_tables import ReviewedDataset
from dataland_qa_lab.dataland import dataset_provider
from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator import NuclearAndGasReportGenerator
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def review_dataset(data_id: str) -> str | None:
    """Review a dataset."""
    dataset = dataset_provider.get_dataset_by_id(data_id)

    existing_entity = get_entity(data_id, ReviewedDataset)

    if existing_entity is None:
        test = ReviewedDataset(data_id=data_id, review_start_time=datetime.now().strftime("%H + 1:%M:%S"))

        add_entity(test)

        data_collection = NuclearAndGasDataCollection(dataset.data)

        relevant_pages_pdf_reader = pages_provider.get_relevant_pages_of_pdf(data_collection)

        readable_text = text_to_doc_intelligence.extract_text_of_pdf(relevant_pages_pdf_reader)

        report = NuclearAndGasReportGenerator().generate_report(relevant_pages=readable_text, dataset=data_collection)

        send_r = config.get_config().dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report(
        data_id=data_id, nuclear_and_gas_data=report
        )

        test.review_end_time = datetime.now().strftime("%H:%M:%S")

        test.review_completed = True

        test.report_id = send_r

        update_entity(test)
    else:
        return
