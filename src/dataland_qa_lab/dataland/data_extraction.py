import io

import pypdf
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, ContentFormat
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

from dataland_qa_lab.utils import config


def get_relevant_page_of_pdf(page: int, full_pdf: pypdf.PdfReader) -> io.BytesIO:
    """Returns the relevant pages as byteStream."""
    partial_pdf_stream = io.BytesIO()
    partial_pdf = pypdf.PdfWriter()

    partial_pdf.add_page(full_pdf.get_page(page - 1))
    partial_pdf.write(partial_pdf_stream)
    partial_pdf_stream.seek(0)

    return partial_pdf_stream


def extract_text_of_pdf(pdf: io.BytesIO) -> AnalyzeResult:
    """Make Text machine readable."""
    conf = config.get_config()
    docintel_cred = AzureKeyCredential(conf.azure_docintel_api_key)
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=conf.azure_docintel_endpoint, credential=docintel_cred
    )

    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout",
        analyze_request=pdf,
        content_type="application/octet-stream",
        output_content_format=ContentFormat.MARKDOWN,
    )
    return poller.result()


def extract_section_426(relevant_document: AnalyzeResult) -> str | None:
    """Get correct values from LLM."""
    conf = config.get_config()
    client = AzureOpenAI(
        api_key=conf.azure_openai_api_key, api_version="2024-07-01-preview", azure_endpoint=conf.azure_openai_endpoint
    )

    deployment_name = "gpt-4o"

    prompt = f"""
    Answer only with 'yes' or 'no'!
    You are an AI research Agent. As the agent, you answer questions briefly, succinctly, and factually.
    Always justify you answer.
    # Safety
    - You **should always** reference factual statements to search results based on [relevant documents]
    - Search results based on [relevant documents] may be incomplete or irrelevant. You do not make assumptions
      on the search results beyond strictly what's returned.
    - If the search results based on [relevant documents] do not contain sufficient information to answer user
      message completely, you respond using the tool 'cannot_answer_question'
    - Your responses should avoid being vague, controversial or off-topic.

    # Task
    Given the information from the [relevant documents], is the company engaged in the research, development,
    demonstration, and deployment of innovative power generation facilities that generate energy from nuclear
    processes with minimal waste from the fuel cycle, finance such activities, or hold risk positions related
    to these activities? Just answer the question with yes or no. The answer should not be longer than 3
    characters, should not include punctation and start with a capital letter.

    # Relevant Documents
    {relevant_document.content}
    """

    initial_openai_response = client.chat.completions.create(
        model=deployment_name,
        temperature=0,
        messages=[
            {"role": "system", "content": prompt},
        ],
    )
    return initial_openai_response.choices[0].message.content
