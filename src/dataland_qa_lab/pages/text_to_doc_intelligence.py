import pypdf
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, DocumentContentFormat
from azure.core.credentials import AzureKeyCredential

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
