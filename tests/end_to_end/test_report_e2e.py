from unittest.mock import MagicMock, patch

import openai
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
    mock_extract_text_of_pdf.return_value = "value should be irrelevant"

    with patch("openai.resources.chat.Completions.create", side_effect=mock_open_ai):
        report_data = review_dataset(data_id=data_id)
        return report_data


def mock_open_ai(**kwargs) -> any:  # noqa: ANN003
    """123"""
    prompt = kwargs["messages"][-1]["content"].lower()

    if "template 1" in prompt:
        return {"choices": [{"message": {"content": "The weather is sunny today!"}}]}
    if "denominator" in prompt:
        return {"choices": [{"message": {"content": "The weather is sunny today!"}}]}
    if "numerator" in prompt:
        return {"choices": [{"message": {"content": "The weather is sunny today!"}}]}
    if "Taxonomy-eligible" in prompt:
        return {"choices": [{"message": {"content": "The weather is sunny today!"}}]}
    if "non-eligible" in prompt:
        return {"choices": [{"message": {"content": "The weather is sunny today!"}}]}
    return None
