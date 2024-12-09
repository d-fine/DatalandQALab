import io
from typing import Any
from unittest import mock

from azure.ai.documentintelligence.models import AnalyzeResult
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice
from pypdf import PdfReader

from dataland_qa_lab.dataland import data_extraction, get_data, provide_test_data
from dataland_qa_lab.utils import config


def test_dataland_connectivity() -> None:
    client = config.get_config().dataland_client
    resolved_companies = client.company_api.get_companies(chunk_size=1)
    assert len(resolved_companies) > 0


def test_dummy_get_data() -> None:
    dataland_client = config.get_config().dataland_client
    company_name = "rwe"
    company_id = provide_test_data.get_company_id(
        company=company_name, dataland_client=dataland_client
    )  # not used method to make merge possible; will be removed later
    data_id = get_data.get_data_id_by_company_id(company_id=company_id)
    data = dataland_client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(data_id=data_id)
    current_values = get_data.get_values_by_data(data=data)
    test = get_data.get_datasource_reference_bytes(data=data)
    assert test is not None
    assert len(current_values) == 6


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


@mock.patch("openai.resources.chat.Completions.create", return_value=build_simple_openai_chat_completion("No"))
@mock.patch(
    "dataland_qa_lab.dataland.data_extraction.extract_text_of_pdf", return_value=create_document_intelligence_mock()
)
def test_dummy_data_extraction(mock_create: Any, mock_extract_text_of_pdf: Any) -> None:  # noqa: ANN401, ARG001
    dataland_client = config.get_config().dataland_client

    dataset = dataland_client.eu_taxonomy_nuclear_and_gas_api.get_company_associated_nuclear_and_gas_data(
        data_id="9ae2300a-db98-4815-abee-152a24cd3039"
    )

    get_data.get_values_by_data(data=dataset)
    data = get_data.get_datasource_reference_bytes(data=dataset)

    dataset_section426 = dataset.data.general.general.nuclear_energy_related_activities_section426
    file_id = dataset_section426.data_source.file_reference
    pdf = dataland_client.documents_api.get_document(file_id)
    pdf_stream = io.BytesIO(pdf)
    pdf_reader = PdfReader(pdf_stream)
    data = data_extraction.get_relevant_page_of_pdf(int(dataset_section426.data_source.page), pdf_reader)
    text = data_extraction.extract_text_of_pdf(data)
    result = data_extraction.extract_section_426(text)
    assert result == "No"
