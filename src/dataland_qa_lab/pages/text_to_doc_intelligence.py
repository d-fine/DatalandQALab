import pypdf
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, DocumentContentFormat
from azure.core.credentials import AzureKeyCredential
from datetime import UTC, datetime, timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError
from dataland_qa_lab.database import database_engine, database_tables
from dataland_qa_lab.utils import config


def extract_text_of_pdf(pdf: pypdf.PdfReader) -> AnalyzeResult:
    """Use Azure Document Intelligence to make text readable for azure open ai."""
    conf = config.get_config()
    docintel_cred = AzureKeyCredential(conf.azure_docintel_api_key)
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=conf.azure_docintel_endpoint, credential=docintel_cred
    )
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout",
        analyze_request=pdf,
        content_type="application/octet-stream",
        output_content_format=DocumentContentFormat.MARKDOWN,
    )
    return poller.result()


def add_document_if_not_exists(data_id: str, relevant_pages_pdf_reader: str) -> str:
    """Adds or updates a markdown document in the database if necessary."""
    session = database_engine.SessionLocal()
    readable_text = None

    now_utc = datetime.now(UTC)
    ger_timezone = timedelta(hours=2) if now_utc.astimezone(timezone(timedelta(hours=1))).dst() else timedelta(hours=1)
    formatted_german_time = (now_utc + ger_timezone).strftime("%Y-%m-%d %H:%M:%S")

    try:
        database_engine.create_tables()
        exist_markdown = session.query(database_tables.ReviewedDatasetMarkdowns).filter_by(data_id=data_id).first()

        if exist_markdown:
            if exist_markdown.relevant_pages_pdf_reader != relevant_pages_pdf_reader:
                readable_text = extract_text_of_pdf(relevant_pages_pdf_reader)
                exist_markdown.markdown_text = readable_text
                exist_markdown.relevant_pages_pdf_reader = relevant_pages_pdf_reader
                exist_markdown.last_updated = formatted_german_time
            else:
                readable_text = exist_markdown.markdown_text
        else:
            readable_text = extract_text_of_pdf(relevant_pages_pdf_reader)
            new_document = database_tables.ReviewedDatasetMarkdowns(
                data_id=data_id,
                markdown_text=readable_text,
                relevant_pages_pdf_reader=relevant_pages_pdf_reader,
                last_saved=formatted_german_time,
                last_updated=formatted_german_time,
            )
            session.add(new_document)
        session.commit()
    except SQLAlchemyError as e:
        database_engine.logger.exception(f"Database error: {e}")
        raise
    finally:
        session.close()
    return readable_text
