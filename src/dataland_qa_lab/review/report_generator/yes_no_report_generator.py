from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_qa.models.nuclear_and_gas_general_general import NuclearAndGasGeneralGeneral
from dataland_qa.models.qa_report_data_point_extended_data_point_yes_no import (
    QaReportDataPointExtendedDataPointYesNo,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review import yes_no_value_generator
from dataland_qa_lab.utils import comparator
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def build_yes_no_report(
    dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult | None
) -> NuclearAndGasGeneralGeneral:
    """Create yes no report."""
    report = NuclearAndGasGeneralGeneral()

    try:
        yes_no_values = yes_no_value_generator.get_yes_no_values_from_report(relevant_pages)
        yes_no_values_from_dataland = data_provider.get_yes_no_values_by_data(data=dataset)
        data_sources = data_provider.get_datasources_of_nuclear_and_gas_yes_no_questions(data=dataset)

        yes_no_data_points = comparator.compare_yes_no_values(yes_no_values, yes_no_values_from_dataland, data_sources)

        for key, value in yes_no_data_points.items():
            setattr(report, key, value)

    except Exception as e:  # noqa: BLE001
        error_message = str(e)
        data_point_report = QaReportDataPointExtendedDataPointYesNo(
            comment=error_message,
            verdict=QaReportDataPointVerdict.QANOTATTEMPTED,
            correctedData=ExtendedDataPointYesNo(),
        )
        for field_name in [
            "nuclear_energy_related_activities_section426",
            "nuclear_energy_related_activities_section427",
            "nuclear_energy_related_activities_section428",
            "fossil_gas_related_activities_section429",
            "fossil_gas_related_activities_section430",
            "fossil_gas_related_activities_section431",
        ]:
            setattr(report, field_name, data_point_report)

    return report
