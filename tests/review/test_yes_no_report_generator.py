from unittest.mock import Mock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice

from dataland_qa_lab.review.report_generator import yes_no_report_generator
from tests.utils.provide_test_data_collection import provide_test_data_collection


def create_document_intelligence_mock() -> AnalyzeResult:
    return AnalyzeResult(content="")


def build_simple_openai_chat_completion() -> ChatCompletion:
    msg = "['Yes', 'No', 'Yes', 'Yes', 'Yes', 'No']"
    return ChatCompletion(
        id="test",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content=msg,
                    role="assistant",
                ),
            )
        ],
        created=0,
        model="test",
        object="chat.completion",
    )


@patch("dataland_qa_lab.review.yes_no_value_generator.get_yes_no_values_from_report")
@patch("dataland_qa_lab.dataland.data_provider.get_yes_no_values_by_data")
@patch("dataland_qa_lab.review.data_provider.get_datasources_of_nuclear_and_gas_yes_no_questions")
def test_compare_yes_no_values(mock_get_yes_no_values: Mock, mock_get_yes_no_values_by_data: Mock, mock_get_yes_no_values_from_report: Mock) -> None:  # noqa: E501
    test_data_collection = provide_test_data_collection()
    mock_get_yes_no_values_from_report.return_value = {
        "nuclear_energy_related_activities_section426": "No",
        "fossil_gas_related_activities_section430": "Yes",
    }
    mock_get_yes_no_values_by_data.return_value = {
        "nuclear_energy_related_activities_section426": "No",
        "fossil_gas_related_activities_section430": "Yes",
    }
    mock_get_yes_no_values.return_value = {
        "nuclear_energy_related_activities_section426": "Source A",
        "fossil_gas_related_activities_section430": "Source B",
    }

    report = yes_no_report_generator.build_yes_no_report(dataset=test_data_collection, relevant_pages="Dummy relevant pages", ai_model="test-model")  # noqa: E501

    nuclear_report = report.nuclear_energy_related_activities_section426
    fossil_report = report.fossil_gas_related_activities_section430
    assert nuclear_report.correctedData.value == "No"
    assert nuclear_report.verdict == QaReportDataPointVerdict.QAACCEPTED
    assert fossil_report.correctedData.value is None
    assert fossil_report.verdict == QaReportDataPointVerdict.QAREJECTED
    assert fossil_report.comment == "Discrepancy in 'fossil_gas_related_activities_section430': YesNo.YES != YesNo.NO."


def test_build_yes_no_report_no_relevant_pages() -> None:
    test_data_collection = provide_test_data_collection()
    report = yes_no_report_generator.build_yes_no_report(dataset=test_data_collection, relevant_pages=None)

    expected_comment = "No relevant pages found"

    assert report.nuclear_energy_related_activities_section426.comment == expected_comment
    assert report.nuclear_energy_related_activities_section426.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert report.fossil_gas_related_activities_section429.comment == expected_comment
    assert report.fossil_gas_related_activities_section429.verdict == QaReportDataPointVerdict.QANOTATTEMPTED


@patch("dataland_qa_lab.review.yes_no_value_generator.get_yes_no_values_from_report")
def test_build_yes_no_report_generator_error(mock_get_yes_no_values: Mock) -> None:
    mock_get_yes_no_values.side_effect = ValueError("Error in get_yes_no_values_from_report")

    test_data_collection = provide_test_data_collection()
    report = yes_no_report_generator.build_yes_no_report(dataset=test_data_collection, relevant_pages="123")

    assert report.nuclear_energy_related_activities_section426.comment == "Error in get_yes_no_values_from_report"
    assert report.nuclear_energy_related_activities_section426.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
    assert report.nuclear_energy_related_activities_section426.correctedData.value is None


@patch("dataland_qa_lab.dataland.data_provider.get_yes_no_values_by_data")
def test_build_yes_no_report_data_provider_error(mock_get_yes_no_values_by_data: Mock, mock_get_yes_no_values_from_report: Mock) -> None:  # noqa: E501
    mock_get_yes_no_values_from_report.return_value = {}
    mock_get_yes_no_values_by_data.side_effect = ValueError("Error in get_yes_no_values_by_data")
    test_data_collection = provide_test_data_collection()
    report = yes_no_report_generator.build_yes_no_report(dataset=test_data_collection, relevant_pages="123")

    assert report.nuclear_energy_related_activities_section426.comment == "Error in get_yes_no_values_by_data"
    assert report.nuclear_energy_related_activities_section426.verdict == QaReportDataPointVerdict.QANOTATTEMPTED
