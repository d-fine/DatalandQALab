from dataland_qa_lab.dataland.dataset_provider import DatasetProvider
from dataland_qa_lab.pages.pages_provider import PagesProvider
from dataland_qa_lab.pages.text_to_doc_intelligence import TextToDocIntelligence
from dataland_qa_lab.review.report_generator import ReportGenerator
from dataland_qa_lab.utils import config


class DatasetReviewer:
    """Not implemented yet."""

    def __init__(self) -> None:
        """Initialize any necessary resources or configurations for the dataset reviewer."""
        self.conf = config.get_config().dataland_client

    def review_dataset(self, data_id: str) -> str | None:
        """Review a dataset."""
        dataset = DatasetProvider().get_dataset_by_id(data_id)

        relevant_pages_pdf_reader = PagesProvider().get_relevant_pages_of_pdf(dataset.data)

        readable_text = TextToDocIntelligence().extract_text_of_pdf(relevant_pages_pdf_reader)

        report = ReportGenerator().generate_report(relevant_pages=readable_text, dataset=dataset.data)

        self.conf.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report(
            data_id=data_id,
            nuclear_and_gas_data=report)
