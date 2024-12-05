from dataland_backend.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_backend.models.nuclear_and_gas_general import NuclearAndGasGeneral
from dataland_backend.models.nuclear_and_gas_general_general import NuclearAndGasGeneralGeneral

from dataland_qa_lab.pages.pages_provider import PagesProvider


def test_get_relevant_pages_of_pdf() -> None:
    test_dataset = NuclearAndGasData(
            general=NuclearAndGasGeneral(
                general=NuclearAndGasGeneralGeneral(
                    nuclearEnergyRelatedActivitiesSection426=ExtendedDataPointYesNo(
                        dataSource=ExtendedDocumentReference(
                            page="21",
                            fileReference="test123")),
                    nuclearEnergyRelatedActivitiesSection427=ExtendedDataPointYesNo(
                        dataSource=ExtendedDocumentReference(
                            page="21",
                            fileReference="test123")),
                    nuclearEnergyRelatedActivitiesSection428=ExtendedDataPointYesNo(
                        dataSource=ExtendedDocumentReference(
                            page="21",
                            fileReference="test123")),
                    fossilGasRelatedActivitiesSection429=ExtendedDataPointYesNo(
                        dataSource=ExtendedDocumentReference(
                            page="21",
                            fileReference="test123")),
                    fossilGasRelatedActivitiesSection430=ExtendedDataPointYesNo(
                        dataSource=ExtendedDocumentReference(
                            page="21",
                            fileReference="test123")),
                    fossilGasRelatedActivitiesSection431=ExtendedDataPointYesNo(
                        dataSource=ExtendedDocumentReference(
                            page="21",
                            fileReference="test123"))
                )
            )
        )
    page_numbers = PagesProvider().get_relevant_pages_of_pdf(test_dataset)

    assert page_numbers[0] == "21"
