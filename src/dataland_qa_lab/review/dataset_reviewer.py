from datetime import UTC, datetime, timedelta, timezone

from dataland_qa.models.qa_report_meta_information import QaReportMetaInformation

from dataland_qa_lab.database.database_engine import add_entity, create_tables, get_entity, update_entity
from dataland_qa_lab.database.database_tables import ReviewedDataset
from dataland_qa_lab.dataland import dataset_provider
from dataland_qa_lab.pages import pages_provider, text_to_doc_intelligence
from dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator import NuclearAndGasReportGenerator
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def review_dataset(data_id: str) -> QaReportMetaInformation | None:
    """Review a dataset."""
    dataset = dataset_provider.get_dataset_by_id(data_id)

    create_tables()

    existing_entity = get_entity(data_id, ReviewedDataset)

    now_utc = datetime.now(UTC)
    ger_timezone = timedelta(hours=2) if now_utc.astimezone(timezone(timedelta(hours=1))).dst() else timedelta(hours=1)
    formatted_german_time1 = (now_utc + ger_timezone).strftime("%Y-%m-%d %H:%M:%S")

    if existing_entity is None:
        review_dataset = ReviewedDataset(data_id=data_id, review_start_time=formatted_german_time1)

        add_entity(review_dataset)

        data_collection = NuclearAndGasDataCollection(dataset.data)

        relevant_pages_pdf_reader = pages_provider.get_relevant_pages_of_pdf(data_collection)

        readable_text = text_to_doc_intelligence.get_markdown_from_dataset(relevant_pages_pdf_reader)

        report = NuclearAndGasReportGenerator().generate_report(relevant_pages=readable_text, dataset=data_collection)

        data = config.get_config().dataland_client.eu_taxonomy_nuclear_gas_qa_api.post_nuclear_and_gas_data_qa_report(
                data_id=data_id, nuclear_and_gas_data=report
            )

        now_utc = datetime.now(UTC)
        if now_utc.astimezone(timezone(timedelta(hours=1))).dst():
            ger_timezone = timedelta(hours=2)
        else:
            ger_timezone = timedelta(hours=1)

        formatted_german_time2 = (now_utc + ger_timezone).strftime("%Y-%m-%d %H:%M:%S")
        review_dataset.review_end_time = formatted_german_time2
        review_dataset.review_completed = True
        review_dataset.report_id = data.qa_report_id

        update_entity(review_dataset)
        return data
    return None
