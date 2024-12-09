import json
from pathlib import Path

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
    page_numbers = PagesProvider().get_relevant_pages_of_nuclear_and_gas_yes_no_questions(test_dataset)

    assert {21, 22}.issubset(page_numbers)


def test_get_relevant_pages_numeric() -> None:
    test_dataset = NuclearAndGasData(
        general=NuclearAndGasGeneral(
            general=NuclearAndGasGeneralGeneral(),
            taxonomyAlignedDenominator=NuclearAndGasGeneralTaxonomyAlignedDenominator(
                nuclearAndGasTaxonomyAlignedCapexDenominator=ExtendedDataPointNuclearAndGasAlignedDenominator(
                    dataSource=ExtendedDocumentReference(page="21", fileReference="test")
                )
            ),
            taxonomyAlignedNumerator=NuclearAndGasGeneralTaxonomyAlignedNumerator(),
            taxonomyEligibleButNotAligned=NuclearAndGasGeneralTaxonomyEligibleButNotAligned(),
            taxonomyNonEligible=NuclearAndGasGeneralTaxonomyNonEligible(
                nuclearAndGasTaxonomyNonEligibleRevenue=ExtendedDataPointNuclearAndGasNonEligible(
                    dataSource=ExtendedDocumentReference(page="22", fileReference="test")
                )
            ),
        )
    )
    page_numbers = PagesProvider().get_relevant_pages_of_numeric(test_dataset)

    assert {21, 22}.issubset(page_numbers)


def test_get_relevant_pages_of_pdf() -> None:
    current_dir = Path(__file__).resolve().parent.parent.parent
    file_path = current_dir / "data" / "jsons" / "covestro.json"
    with Path.open(file_path) as file:
        data = json.load(file)

    file_ref = data["data"]["general"]["general"]["referencedReports"]["covestro-ar23-entire"]["fileReference"]

    test_dataset = NuclearAndGasData(
        general=NuclearAndGasGeneral(
            general=NuclearAndGasGeneralGeneral(
                nuclearEnergyRelatedActivitiesSection426=ExtendedDataPointYesNo(
                    dataSource=ExtendedDocumentReference(page="21", fileReference=file_ref)
                ),
                fossilGasRelatedActivitiesSection430=ExtendedDataPointYesNo(
                    dataSource=ExtendedDocumentReference(page="22", fileReference=file_ref)
                ),
            ),
            taxonomyAlignedDenominator=NuclearAndGasGeneralTaxonomyAlignedDenominator(
                nuclearAndGasTaxonomyAlignedCapexDenominator=ExtendedDataPointNuclearAndGasAlignedDenominator(
                    dataSource=ExtendedDocumentReference(page="21", fileReference=file_ref)
                )
            ),
            taxonomyAlignedNumerator=NuclearAndGasGeneralTaxonomyAlignedNumerator(),
            taxonomyEligibleButNotAligned=NuclearAndGasGeneralTaxonomyEligibleButNotAligned(),
            taxonomyNonEligible=NuclearAndGasGeneralTaxonomyNonEligible(
                nuclearAndGasTaxonomyNonEligibleRevenue=ExtendedDataPointNuclearAndGasNonEligible(
                    dataSource=ExtendedDocumentReference(page="22", fileReference=file_ref)
                )
            ),
        )
    )

    pages = PagesProvider().get_relevant_pages_of_pdf(test_dataset)

    assert pages is not None
