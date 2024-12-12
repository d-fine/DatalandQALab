import json
from pathlib import Path

from dataland_backend.models.extended_data_point_nuclear_and_gas_aligned_denominator import (
    ExtendedDataPointNuclearAndGasAlignedDenominator,
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

from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def provide_test_data_collection() -> NuclearAndGasDataCollection:
    current_dir = Path(__file__).resolve().parent.parent.parent
    file_path = current_dir / "data" / "jsons" / "covestro.json"
    with Path.open(file_path) as file:
        data = json.load(file)

    file_ref = data["data"]["general"]["general"]["referencedReports"]["covestro-ar23-entire"]["fileReference"]

    return NuclearAndGasDataCollection(
        NuclearAndGasData(
            general=NuclearAndGasGeneral(
                general=NuclearAndGasGeneralGeneral(
                    nuclearEnergyRelatedActivitiesSection426=ExtendedDataPointYesNo(
                        value="Yes", dataSource=ExtendedDocumentReference(page="21", fileReference=file_ref)
                    ),
                    fossilGasRelatedActivitiesSection430=ExtendedDataPointYesNo(
                        value="No", dataSource=ExtendedDocumentReference(page="22", fileReference=file_ref)
                    ),
                    fossilGasRelatedActivitiesSection431=ExtendedDataPointYesNo(
                        dataSource=ExtendedDocumentReference(
                            page="22", tag_name="d-fine", fileName="test-file", fileReference=file_ref
                        )
                    ),
                ),
                taxonomyAlignedDenominator=NuclearAndGasGeneralTaxonomyAlignedDenominator(
                    nuclearAndGasTaxonomyAlignedCapexDenominator=ExtendedDataPointNuclearAndGasAlignedDenominator(
                        dataSource=ExtendedDocumentReference(
                            page="31", tag_name="d-fine", fileName="test-file", fileReference=file_ref
                        )
                    )
                ),
                taxonomyAlignedNumerator=NuclearAndGasGeneralTaxonomyAlignedNumerator(),
                taxonomyEligibleButNotAligned=NuclearAndGasGeneralTaxonomyEligibleButNotAligned(),
                taxonomyNonEligible=NuclearAndGasGeneralTaxonomyNonEligible(),
            )
        )
    )
