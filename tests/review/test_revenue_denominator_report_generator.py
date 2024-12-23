import pytest
from azure.ai.documentintelligence.models import AnalyzeResult

from dataland_qa_lab.dataland.dataset_provider import get_dataset_by_id
from dataland_qa_lab.pages.pages_provider import get_relevant_pages_of_pdf
from dataland_qa_lab.pages.text_to_doc_intelligence import extract_text_of_pdf
from dataland_qa_lab.review.report_generator.nuclear_and_gas_report_generator import NuclearAndGasReportGenerator
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection
from tests.utils.provide_example_qa_report import provide_example_qa_report

dataset, qa_report = provide_example_qa_report()


@pytest.fixture
def provide_test_data_() -> tuple[NuclearAndGasDataCollection, AnalyzeResult]:
    dataset_id = "fae59f2e-c438-4457-9a74-55c0db006fee"
    dataset = get_dataset_by_id(dataset_id).data

    relevant_pages = get_relevant_pages_of_pdf(dataset)
    return NuclearAndGasDataCollection(dataset), extract_text_of_pdf(relevant_pages)


def test_build_report_frame() -> None:
    denominator = NuclearAndGasReportGenerator.build_report_frame(dataset, qa_report)

    assert denominator is not None
    assert denominator.nuclearAndGasTaxonomyAlignedRevenueDenominator is not None
    assert denominator.nuclearAndGasTaxonomyAlignedCapexDenominator is not None
