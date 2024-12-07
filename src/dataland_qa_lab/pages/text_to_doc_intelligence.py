import pypdf
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, ContentFormat
from azure.core.credentials import AzureKeyCredential

from dataland_qa_lab.utils import config


class TextToDocIntelligence:
    """Make text machine readable."""

    def __init__(self) -> None:
        """Text."""
        self.conf = config.get_config()

    def extract_text_of_pdf(self, pdf: pypdf.PdfReader) -> AnalyzeResult:
        """Use Azure Document Intelligence to make text readable for azure open ai."""
        docintel_cred = AzureKeyCredential(self.conf.azure_docintel_api_key)
        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=self.conf.azure_docintel_endpoint, credential=docintel_cred
        )

        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout",
            analyze_request=pdf,
            content_type="application/octet-stream",
            output_content_format=ContentFormat.MARKDOWN,
        )
        return poller.result()
