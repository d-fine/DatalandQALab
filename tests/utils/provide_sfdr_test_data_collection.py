from dataland_backend.models.extended_data_point_big_decimal import ExtendedDataPointBigDecimal
from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
from dataland_backend.models.sfdr_data import SfdrData
from dataland_backend.models.sfdr_environmental import SfdrEnvironmental
from dataland_backend.models.sfdr_environmental_greenhouse_gas_emissions import SfdrEnvironmentalGreenhouseGasEmissions

from dataland_qa_lab.utils.sfdr_data_collection import SFDRDataCollection


def provide_sfdr_test_data_collection() -> SFDRDataCollection:
    """Provide test data for SFDRDataCollection."""
    return SFDRDataCollection(
        SfdrData(
            environmental=SfdrEnvironmental(
                greenhouse_gas_emissions=SfdrEnvironmentalGreenhouseGasEmissions(
                    scope1_ghg_emissions_in_tonnes=ExtendedDataPointBigDecimal(
                        value=12345.67,
                        data_source=ExtendedDocumentReference(file_reference="sfdr-test-file-ref", page="45"),
                    )
                )
            )
        )
    )
