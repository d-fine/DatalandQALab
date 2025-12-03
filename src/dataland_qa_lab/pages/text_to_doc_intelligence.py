import logging

import pypdf
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentContentFormat
from azure.core.credentials import AzureKeyCredential

from dataland_qa_lab.database.database_engine import add_entity, get_entity
from dataland_qa_lab.database.database_tables import ReviewedDatasetMarkdowns
from dataland_qa_lab.utils import config
from dataland_qa_lab.utils.datetime_helper import get_german_time_as_string

logger = logging.getLogger(__name__)
config = config.get_config()


def old_extract_text_of_pdf(pdf: pypdf.PdfReader) -> str:
    """Use Azure Document Intelligence to make text readable for azure open ai."""
    docintel_cred = AzureKeyCredential(config.azure_docintel_api_key)
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=config.azure_docintel_endpoint, credential=docintel_cred
    )

    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout",
        body=pdf,
        content_type="application/octet-stream",
        output_content_format=DocumentContentFormat.MARKDOWN,
    )
    return poller.result().content


def old_get_markdown_from_dataset(
    data_id: str, relevant_pages_pdf_reader: pypdf.PdfReader, page_numbers: list[int]
) -> str:
    """Adds or updates a markdown document in the database if necessary and returns it."""
    readable_text = None

    german_time = get_german_time_as_string()

    exist_markdown = get_entity(
        ReviewedDatasetMarkdowns,
        data_id=data_id,
    )

    if exist_markdown:
        readable_text = exist_markdown.markdown_text
    else:
        readable_text = old_extract_text_of_pdf(relevant_pages_pdf_reader)

        if readable_text is None:
            return None

        new_document = ReviewedDatasetMarkdowns(
            data_id=data_id,
            markdown_text=readable_text,
            page_numbers=page_numbers,
            last_saved=german_time,
            last_updated=german_time,
        )

        add_entity(new_document)

    logger.debug("Markdown extracted from the relevant pages.")

    return readable_text


# new method for the new validation flow


def extract_pdf(pdf) -> str:  # noqa: ANN001
    """Use Azure Document Intelligence to make text readable for azure open ai."""
    docintel_cred = AzureKeyCredential(config.azure_docintel_api_key)
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=config.azure_docintel_endpoint, credential=docintel_cred
    )
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout",
        body=pdf,
        content_type="application/octet-stream",
        output_content_format=DocumentContentFormat.MARKDOWN,
    )
    return poller.result().content
