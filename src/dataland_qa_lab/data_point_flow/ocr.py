import asyncio
import io
import logging

import async_lru
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentContentFormat
from azure.core.credentials import AzureKeyCredential

from dataland_qa_lab.data_point_flow import ocr
from dataland_qa_lab.database import database_engine, database_tables
from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)
config = config.get_config()

_lock_map = {}
_lock_map_lock = asyncio.Lock()


def get_lock_for(key):  # noqa: ANN001, ANN201
    """Return a per-key lock, creating it if needed."""

    async def _get():  # noqa: ANN202
        async with _lock_map_lock:
            if key not in _lock_map:
                _lock_map[key] = asyncio.Lock()
            return _lock_map[key]

    return _get()


@async_lru.alru_cache
async def run_ocr_on_document(file_name: str, file_reference: str, page: int, document: io.BytesIO) -> str:
    """Run OCR on the given PDF document and return the extracted text."""
    logger.info("Running OCR on document with reference ID: %s, page: %d", file_reference, page)

    key = (file_name, file_reference, page)
    lock = await get_lock_for(key)

    async with lock:
        cached_document = database_engine.get_entity(
            database_tables.CachedDocument, file_reference=file_reference, page=page
        )

        if cached_document:
            return cached_document.ocr_output

        markdown = ocr.extract_pdf(document)

        database_engine.add_entity(
            database_tables.CachedDocument(
                file_name=file_name,
                file_reference=file_reference,
                ocr_output=markdown,
                page=page,
            )
        )
        return markdown


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
