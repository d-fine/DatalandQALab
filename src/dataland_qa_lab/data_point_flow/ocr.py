import logging

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentContentFormat
from azure.core.credentials import AzureKeyCredential

from dataland_qa_lab.utils import config

logger = logging.getLogger(__name__)
config = config.get_config()


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
