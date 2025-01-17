from dataland_qa_lab.dataland import dataset_provider
from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator import NuclearAndGasReportGenerator
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def review_dataset(data_id: str) -> str | None:
    """Review a dataset."""
    dataset = dataset_provider.get_dataset_by_id(data_id)

    data_collection = NuclearAndGasDataCollection(dataset.data)

    page_numbers = pages_provider.get_relevant_page_numbers(data_collection)

    relevant_pages_pdf_reader = pages_provider.get_relevant_pages_of_pdf(data_collection)

    readable_text = text_to_doc_intelligence.get_markdown_from_dataset(
        data_id=data_id, page_numbers=page_numbers, relevant_pages_pdf_reader=relevant_pages_pdf_reader
    )

    report = NuclearAndGasReportGenerator().generate_report(relevant_pages=readable_text, dataset=data_collection)

    config.get_config().dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report(
        data_id=data_id, nuclear_and_gas_data=report
    )
