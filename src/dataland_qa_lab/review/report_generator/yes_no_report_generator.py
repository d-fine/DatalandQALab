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
    dataset: NuclearAndGasDataCollection, relevant_pages: str | None, ai_model: str | None = None
) -> NuclearAndGasGeneralGeneral:
    """Create yes no report."""
    report = NuclearAndGasGeneralGeneral()

    try:
        if relevant_pages is None:
            create_not_attempted_report(report, "No relevant pages found", dataset=dataset)
            return report

        yes_no_values = yes_no_value_generator.get_yes_no_values_from_report(relevant_pages, ai_model=ai_model)
        yes_no_values_from_dataland = data_provider.get_yes_no_values_by_data(data=dataset)
        data_sources = data_provider.get_datasources_of_nuclear_and_gas_yes_no_questions(data=dataset)

        valid_keys = data_sources.keys()

        yes_no_data_points = comparator.compare_yes_no_values(yes_no_values, yes_no_values_from_dataland, data_sources)

        for key in valid_keys:
            if key in yes_no_data_points:
                setattr(report, key, yes_no_data_points[key])

    except Exception as e:  # noqa: BLE001
        error_message = str(e)
        create_not_attempted_report(report, error_message, dataset=dataset)

    return report


def create_not_attempted_report(
    report: NuclearAndGasGeneralGeneral, error_message: str, dataset: NuclearAndGasDataCollection
) -> None:
    """Populate the report with 'not attempted' data points, based on existing dataset keys."""
    data_point_report = QaReportDataPointExtendedDataPointYesNo(
        comment=error_message,
        verdict=QaReportDataPointVerdict.QANOTATTEMPTED,
        corrected_data=ExtendedDataPointYesNo(),
    )
    data_sources_error = None
    try:
        data_sources = data_provider.get_datasources_of_nuclear_and_gas_yes_no_questions(data=dataset)
        valid_field_names = data_sources.keys()
    except Exception as e:  # noqa: BLE001
        data_sources_error = str(e)
        valid_field_names = []
    if valid_field_names:
        for field_name in valid_field_names:
            setattr(report, field_name, data_point_report)
    else:
        error_message = (
            "Failed to retrieve valid field names for not attempted report. Original error: " + data_sources_error
        )
        error_data_point = yes_no_value_generator.create_error_data_point(error_message)
        fallback_field_name = "nuclear_energy_related_activities_section426"
        setattr(report, fallback_field_name, error_data_point)
