from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_qa.models.nuclear_and_gas_general_general import NuclearAndGasGeneralGeneral
from dataland_qa.models.nuclear_and_gas_general_taxonomy_aligned_numerator import (
    NuclearAndGasGeneralTaxonomyAlignedNumerator,
)
from dataland_qa.models.qa_report_data_point_extended_data_point_yes_no import (
    QaReportDataPointExtendedDataPointYesNo,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review import yes_no_value_generator
from dataland_qa_lab.utils.doc_ref_to_qa_ref_mapper import map_doc_ref_to_qa_doc_ref
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def build_yes_no_report(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult
) -> NuclearAndGasGeneralTaxonomyAlignedNumerator:
    """Create yes no report."""
    report = NuclearAndGasGeneralGeneral()
    yes_no_data_points = compare_yes_no_values(dataset=dataset, relevant_pages=relevant_pages)
    for key, value in yes_no_data_points.items():
        setattr(report, key, value)


def compare_yes_no_values(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult
) -> dict[str, QaReportDataPointExtendedDataPointYesNo | None]:
    """Build first yes no data point."""
    yes_no_values = yes_no_value_generator.get_yes_no_values_from_report(relevant_pages)
    yes_no_values_from_dataland = data_provider.get_yes_no_values_by_data(data=dataset)
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_yes_no_questions(data=dataset)
    qa_data_points = {}

    for field_name, dataland_value in yes_no_values_from_dataland.items():
        corrected_value = yes_no_values.get(field_name)
        data_source = data_sources.get(field_name)

        if corrected_value != dataland_value:
            qa_data_points[field_name] = QaReportDataPointExtendedDataPointYesNo(
                comment="tbd",
                verdict=QaReportDataPointVerdict.QAREJECTED,
                correctedData=ExtendedDataPointYesNo(
                    value=corrected_value,
                    quality="Incomplete",
                    comment=(f"Discrepancy in '{field_name}': {dataland_value} != {corrected_value}."),
                    dataSource=map_doc_ref_to_qa_doc_ref(data_source),
                ),
            )
        else:
            qa_data_points[field_name] = QaReportDataPointExtendedDataPointYesNo(
                comment="Geprüft durch AzureOpenAI",
                verdict=QaReportDataPointVerdict.QAACCEPTED,
                correctedData=ExtendedDataPointYesNo(),
            )

    return qa_data_points
