import io
from typing import Any
from unittest import mock

from azure.ai.documentintelligence.models import AnalyzeResult
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice
from pypdf import PdfReader

import dataland_qa_lab.dataland.data_extraction as da
import dataland_qa_lab.dataland.get_data as qa
from dataland_qa_lab.utils import config


def test_dataland_connectivity() -> None:
    client = config.get_config().dataland_client
    resolved_companies = client.company_api.get_companies(chunk_size=1)
    assert len(resolved_companies) > 0


def test_dummy_get_data() -> None:
    company_id = "4423c691-0436-423f-abcb-0a08127ee848"
    year = "2024"
    qa.get_all_company_datasets(company_id=company_id)
    qa.get_data_id_by_year(company_id=company_id, year=year)
    qa.get_dataset_by_year(company_id=company_id, year=year)
    qa.get_value1_by_year(company_id=company_id, year=year)
    test = qa.get_datasource_reference_bytes(company_id=company_id, year=year)

    assert test is not None


def create_document_intelligence_mock() -> AnalyzeResult:
    return AnalyzeResult(content="")


def build_simple_openai_chat_completion(message: str) -> ChatCompletion:
    return ChatCompletion(
        id="test",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content=message,
                    role="assistant",
                ),
            )
        ],
        created=0,
        model="test",
        object="chat.completion",
    )


@mock.patch("openai.resources.completions.Completions.create", return_value=build_simple_openai_chat_completion("No"))
@mock.patch(
    "dataland_qa_lab.dataland.data_extraction.extract_text_of_pdf", return_value=create_document_intelligence_mock()
)  # noqa: E501
def test_dummy_data_extraction(mock_create_: Any, mock_extract_text_of_pdf: Any) -> None:  # noqa: ANN401, ARG001
    dataland_client = da.get_config().dataland_client
    dataset_by_year = qa.get_dataset_by_year(company_id="4423c691-0436-423f-abcb-0a08127ee848", year="2024")

    dataset_section426 = dataset_by_year.data.general.general.nuclear_energy_related_activities_section426
    file_id = dataset_section426.data_source.file_reference

    pdf = dataland_client.documents_api.get_document(file_id)
    pdf_stream = io.BytesIO(pdf)
    pdf_reader = PdfReader(pdf_stream)

    data = da.get_relevant_page_of_pdf(int(dataset_section426.data_source.page), pdf_reader)
    text = da.extract_text_of_pdf(data)
    result = da.extract_section_426(text)

    assert result is not None
