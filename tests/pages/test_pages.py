from unittest import mock

from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_backend.models.extended_data_point_nuclear_and_gas_aligned_denominator import (
    ExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_backend.models.extended_data_point_nuclear_and_gas_non_eligible import (
    ExtendedDataPointNuclearAndGasNonEligible,
)
from dataland_backend.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_backend.models.nuclear_and_gas_general import NuclearAndGasGeneral
from dataland_backend.models.nuclear_and_gas_general_general import NuclearAndGasGeneralGeneral
from dataland_backend.models.nuclear_and_gas_general_taxonomy_aligned_denominator import (
    NuclearAndGasGeneralTaxonomyAlignedDenominator,
)
from dataland_backend.models.nuclear_and_gas_general_taxonomy_aligned_numerator import (
    NuclearAndGasGeneralTaxonomyAlignedNumerator,
)
from dataland_backend.models.nuclear_and_gas_general_taxonomy_eligible_but_not_aligned import (
    NuclearAndGasGeneralTaxonomyEligibleButNotAligned,
)
from dataland_backend.models.nuclear_and_gas_general_taxonomy_non_eligible import (
    NuclearAndGasGeneralTaxonomyNonEligible,
)

from dataland_qa_lab.pages.pages_provider import PagesProvider


def test_get_relevant_pages_yes_no() -> None:
    test_dataset = NuclearAndGasData(
        general=NuclearAndGasGeneral(
            general=NuclearAndGasGeneralGeneral(
                nuclearEnergyRelatedActivitiesSection426=ExtendedDataPointYesNo(
                    dataSource=ExtendedDocumentReference(page="21", fileReference="test")
                ),
                fossilGasRelatedActivitiesSection430=ExtendedDataPointYesNo(
                    dataSource=ExtendedDocumentReference(page="22", fileReference="test")
                ),
            )
        )
    )
    page_numbers = PagesProvider().get_relevant_pages_of_yes_no(test_dataset)

    assert {21, 22}.issubset(page_numbers)


def test_get_relevant_pages_numeric() -> None:
    test_dataset = NuclearAndGasData(
        general=NuclearAndGasGeneral(
            general=NuclearAndGasGeneralGeneral(),
            taxonomyAlignedDenominator=NuclearAndGasGeneralTaxonomyAlignedDenominator(
                nuclearAndGasTaxonomyAlignedCapexDenominator=ExtendedDataPointNuclearAndGasAlignedDenominator(
                    dataSource=ExtendedDocumentReference(
                        page="21",
                        fileReference="test")
                )
            ),
            taxonomyAlignedNumerator=NuclearAndGasGeneralTaxonomyAlignedNumerator(),
            taxonomyEligibleButNotAligned=NuclearAndGasGeneralTaxonomyEligibleButNotAligned(),
            taxonomyNonEligible=NuclearAndGasGeneralTaxonomyNonEligible(
                nuclearAndGasTaxonomyNonEligibleRevenue=ExtendedDataPointNuclearAndGasNonEligible(
                     dataSource=ExtendedDocumentReference(
                        page="22",
                        fileReference="test"
                    )
                )
            )
        )
    )
    page_numbers = PagesProvider().get_relevant_pages_of_numeric(test_dataset)

    assert {21, 22}.issubset(page_numbers)


# def create_document_intelligence_mock() -> AnalyzeResult:
#     return AnalyzeResult(content="")


# @mock.patch(
#     "dataland_qa_lab.pages.text_to_doc_intelligence.extract_text_of_pdf",
#     return_value=create_document_intelligence_mock()
# )
# def test_extract_text_of_pdf() -> None:
#     extractor = TextToDocIntelligence()
#     extractor.extract_text_of_pdf()
