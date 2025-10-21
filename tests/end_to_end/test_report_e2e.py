import json
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

import mock_constants
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict
from dataland_qa.models.qa_report_meta_information import QaReportMetaInformation

from dataland_qa_lab.database.database_engine import delete_entity
from dataland_qa_lab.database.database_tables import ReviewedDataset
from dataland_qa_lab.dataland.provide_test_data import get_company_id, upload_dataset, upload_pdf
from dataland_qa_lab.review.dataset_reviewer import review_dataset
from dataland_qa_lab.utils import config


def test_report_generator_end_to_end() -> None:
    """
    This test is supposed to test the entire process of generating a Quality-Assurance-Report for a
    EU Taxonomy Nuclear and Gas dataset from dataland.com.
    Only the communication to Azure is mocked, all other components and their interactions
    should be tested during this test.
    """
    data_id = upload_test_dataset()
    delete_entity(data_id, ReviewedDataset)
    report_id = mocked_review_dataset(data_id)
    report_data = config.get_config().dataland_client.eu_taxonomy_nuclear_gas_qa_api.get_nuclear_and_gas_data_qa_report(
        data_id=data_id, qa_report_id=report_id
    )
    report_data_dict = report_data.to_dict()

    data_yes_no_426 = report_data_dict["report"]["general"]["general"]["nuclearEnergyRelatedActivitiesSection426"]

    assert data_yes_no_426["comment"] == "Reviewed by AzureOpenAI"
    assert QaReportDataPointVerdict.QAACCEPTED in data_yes_no_426["verdict"]
    assert data_yes_no_426["correctedData"] == {}

    data_yes_no_429 = report_data_dict["report"]["general"]["general"]["fossilGasRelatedActivitiesSection429"]

    assert (
        data_yes_no_429["comment"]
        == "Discrepancy in 'fossil_gas_related_activities_section429': YesNo.NO != YesNo.YES."
    )
    assert QaReportDataPointVerdict.QAREJECTED in data_yes_no_429["verdict"]
    assert data_yes_no_429["correctedData"] == {
        "value": "Yes",
        "quality": "Reported",
        "comment": "",
        "dataSource": ANY,
    }

    data_taxonomy_aligned_revenue_denominator = report_data_dict["report"]["general"]["taxonomyAlignedDenominator"][
        "nuclearAndGasTaxonomyAlignedRevenueDenominator"
    ]

    assert (
        data_taxonomy_aligned_revenue_denominator["comment"]
        == "Discrepancy in 'taxonomy_aligned_share_denominator_n_and_g426': 15 != 0.0."
    )
    assert QaReportDataPointVerdict.QAREJECTED in data_taxonomy_aligned_revenue_denominator["verdict"]
    assert data_taxonomy_aligned_revenue_denominator["correctedData"] == {
        "value": {
            "taxonomyAlignedShareDenominatorNAndG426": {"mitigationAndAdaptation": 0.0},
            "taxonomyAlignedShareDenominatorNAndG427": ANY,
            "taxonomyAlignedShareDenominatorNAndG428": ANY,
            "taxonomyAlignedShareDenominatorNAndG429": ANY,
            "taxonomyAlignedShareDenominatorNAndG430": ANY,
            "taxonomyAlignedShareDenominatorNAndG431": ANY,
            "taxonomyAlignedShareDenominatorOtherActivities": ANY,
            "taxonomyAlignedShareDenominator": ANY,
        },
        "quality": "Reported",
        "comment": "",
    }

    data_taxonomy_eligible_but_not_aligned = report_data_dict["report"]["general"]["taxonomyEligibleButNotAligned"][
        "nuclearAndGasTaxonomyEligibleButNotAlignedCapex"
    ]

    assert not data_taxonomy_eligible_but_not_aligned["comment"]
    assert QaReportDataPointVerdict.QAACCEPTED in data_taxonomy_eligible_but_not_aligned["verdict"]
    assert data_taxonomy_eligible_but_not_aligned["correctedData"] == {}


@patch("dataland_qa_lab.pages.text_to_doc_intelligence.extract_text_of_pdf")
@patch("dataland_qa_lab.database.database_engine.get_entity")
def mocked_review_dataset(
    data_id: str,
    mock_get_entity: MagicMock,
    mock_extract_text_of_pdf: MagicMock,
) -> QaReportMetaInformation:
    """Review the dataset with mocked Azure calls."""
    mock_extract_text_of_pdf.return_value = mock_constants.E2E_AZURE_DOCUMENT_INTELLIGENCE_MOCK
    mock_get_entity.return_value = None
    with patch("openai.resources.chat.Completions.create", side_effect=mock_open_ai):
        with patch("dataland_qa_lab.review.dataset_reviewer.send_alert_message") as mocked_post:
            mocked_post.return_value = None

            report_data = review_dataset(data_id=data_id, force_review=True)
        return report_data


def mock_open_ai(**kwargs: any) -> any:
    """Return the result of the Azure OpenAI call based on keywords in the prompt."""
    prompt = kwargs["messages"][-1]["content"].lower()

    mock_chat_completion = None
    if "template 1" in prompt:
        mock_chat_completion = mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_1
    if "template 2 (revenue)" in prompt:
        mock_chat_completion = mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_2_REVENUE
    if "template 2 (capex)" in prompt:
        mock_chat_completion = mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_2_CAPEX
    if "template 3 (revenue)" in prompt:
        mock_chat_completion = mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_3_REVENUE
    if "template 3 (capex)" in prompt:
        mock_chat_completion = mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_3_CAPEX
    if "template 4 (revenue)" in prompt:
        mock_chat_completion = mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_4_REVENUE
    if "template 4 (capex)" in prompt:
        mock_chat_completion = mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_4_CAPEX
    if "template 5 (revenue)" in prompt:
        mock_chat_completion = mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_5_REVENUE
    if "template 5 (capex)" in prompt:
        mock_chat_completion = mock_constants.E2E_AZURE_OPEN_AI_TEMPLATE_5_CAPEX

    return mock_chat_completion


def upload_test_dataset() -> str:
    """Upload test dataset and save its data id"""

    dataland_client = config.get_config().dataland_client
    project_root = Path(__file__).resolve().parent.parent.parent
    pdf_path = project_root / "data" / "pdfs"
    json_path = project_root / "data" / "jsons"

    upload_pdf(
        pdf_path=pdf_path,
        pdf_id="9c0a555a29683aedd2cd50ff7e837181a7fbb2d1c567d336897e2356fc17a595",
        company="enbw",
        dataland_client=dataland_client,
    )

    company_id = get_company_id(company="enbw", dataland_client=dataland_client)

    json_file_path = json_path / "enbw.json"

    with json_file_path.open(encoding="utf-8") as f:
        json_data = json.load(f)
    json_data["companyId"] = company_id
    json_str = json.dumps(json_data, indent=4)

    data_id = upload_dataset(
        company_id=company_id, json_str=json_str, dataland_client=dataland_client, reporting_period="2020"
    )

    return data_id
