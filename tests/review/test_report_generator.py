from unittest.mock import Mock, patch

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_backend.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_backend.models.nuclear_and_gas_general import NuclearAndGasGeneral
from dataland_backend.models.nuclear_and_gas_general_general import NuclearAndGasGeneralGeneral
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage, Choice

from dataland_qa_lab.review.report_generator import ReportGenerator


def test_build_report_frame() -> None:
    report_frame = ReportGenerator().build_report_frame()

    assert report_frame is not None
    assert report_frame.general.taxonomy_aligned_denominator is not None


def create_document_intelligence_mock() -> AnalyzeResult:
    return AnalyzeResult(content="")


def build_simple_openai_chat_completion() -> ChatCompletion:
    msg = "Yes No Yes Yes Yes No"
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


@patch("openai.resources.chat.Completions.create", return_value=build_simple_openai_chat_completion())
def test_compare_yes_no_values(_mock_create: Mock) -> None:  # noqa: PT019
    test_dataset = NuclearAndGasData(
        general=NuclearAndGasGeneral(
            general=NuclearAndGasGeneralGeneral(
                nuclearEnergyRelatedActivitiesSection426=ExtendedDataPointYesNo(value="Yes"),
                fossilGasRelatedActivitiesSection430=ExtendedDataPointYesNo(value="No"),
            )
        )
    )

    corrected_values = ReportGenerator().compare_yes_no_values(dataset=test_dataset, relevant_pages=AnalyzeResult())
    assert corrected_values[0].corrected_data.value is None
    assert corrected_values[0].comment == "Geprüft durch AzureOpenAI"
    assert corrected_values[4].corrected_data.value == "Yes"


@patch("openai.resources.chat.Completions.create", return_value=build_simple_openai_chat_completion())
def test_generate_report(_mock_create: Mock) -> None:  # noqa: PT019
    test_dataset = NuclearAndGasData(
        general=NuclearAndGasGeneral(
            general=NuclearAndGasGeneralGeneral(
                nuclearEnergyRelatedActivitiesSection426=ExtendedDataPointYesNo(value="Yes"),
                fossilGasRelatedActivitiesSection430=ExtendedDataPointYesNo(value="No"),
            )
        )
    )

    report = ReportGenerator().generate_report(relevant_pages=AnalyzeResult(), dataset=test_dataset)

    assert report is not None
    assert report.general.general.fossil_gas_related_activities_section430.corrected_data.value == "Yes"
