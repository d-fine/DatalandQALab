from unittest.mock import MagicMock, patch

import mock_constants
from dataland_qa.models.qa_report_meta_information import QaReportMetaInformation

from dataland_qa_lab.review.dataset_reviewer import review_dataset


def test_report_generator_end_to_end() -> None:
    """
    This test is supposed to test the entire process of generating a Quality-Assurance-Report for a
    EU Taxonomy Nuclear and Gas dataset from dataland.com.
    Only the communication to Azure is mocked, all other components and their interactions
    should be tested during this test.
    """

    # upload test dataset
    data_id = "d026358f-39e0-4d00-8395-2ce821aa38ec"

    mocked_review_dataset(data_id)
    # test if all error is test dataset were found


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.extract_text_of_pdf")
def mocked_review_dataset(
    data_id: str,
    mock_extract_text_of_pdf: MagicMock,
) -> QaReportMetaInformation:
    """Review the dataset with mocked Azure calls."""
    mock_extract_text_of_pdf.return_value = mock_constants.E2E_AZURE_DOCUMENT_INTELLIGENCE_MOCK

    with patch("openai.resources.chat.Completions.create", side_effect=mock_open_ai):
        report_data = review_dataset(data_id=data_id)
        print(report_data)
        return report_data


def mock_open_ai(**kwargs) -> any:  # noqa: ANN003
    """Return the result of the Azure OpenAI call based on keywords in the prompt."""
    prompt = kwargs["messages"][-1]["content"].lower()

    if "template 1" in prompt:
        return mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_1
    if "template 2 (revenue)" in prompt:
        return mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_2_REVENUE
    if "template 2 (capex)" in prompt:
        return mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_2_CAPEX
    if "template 3 (revenue)" in prompt:
        return mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_3_REVENUE
    if "template 3 (capex)" in prompt:
        return mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_3_CAPEX
    if "template 4 (revenue)" in prompt:
        return mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_4_REVENUE
    if "template 4 (capex)" in prompt:
        return mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_4_CAPEX
    if "template 5 (revenue)" in prompt:
        return mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_5_REVENUE
    if "template 5 (capex)" in prompt:
        return mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_5_CAPEX

    return None
