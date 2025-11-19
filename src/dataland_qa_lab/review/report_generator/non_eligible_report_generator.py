from dataland_qa.models.extended_data_point_nuclear_and_gas_non_eligible import (
    ExtendedDataPointNuclearAndGasNonEligible,
)
from dataland_qa.models.extended_document_reference import ExtendedDocumentReference
from dataland_qa.models.nuclear_and_gas_general_taxonomy_non_eligible import NuclearAndGasGeneralTaxonomyNonEligible
from dataland_qa.models.qa_report_data_point_extended_data_point_nuclear_and_gas_non_eligible import (
    QaReportDataPointExtendedDataPointNuclearAndGasNonEligible,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review.numeric_value_generator import NumericValueGenerator
from dataland_qa_lab.utils import comparator
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


def build_taxonomy_non_eligible_report(
    dataset: NuclearAndGasDataCollection, relevant_pages: str | None, ai_model: str | None = None,
) -> NuclearAndGasGeneralTaxonomyNonEligible:
    """Create Report Frame for the Nuclear and Gas General Taxonomy Non Eligible."""
    return NuclearAndGasGeneralTaxonomyNonEligible(
        nuclearAndGasTaxonomyNonEligibleRevenue=build_non_eligible_report_frame(dataset, relevant_pages, "Revenue",
             ai_model=ai_model),
        nuclearAndGasTaxonomyNonEligibleCapex=build_non_eligible_report_frame(dataset, relevant_pages, "CapEx",
            ai_model=ai_model),
    )


def build_non_eligible_report_frame(
    dataset: NuclearAndGasDataCollection, relevant_pages: str | None, kpi: str, ai_model: str | None = None,
) -> QaReportDataPointExtendedDataPointNuclearAndGasNonEligible:
    """Build report frame for the revenue non_eligible."""
    if relevant_pages is None:
        return create_not_attempted_report("No relevant pages found")
    try:
        prompted_values = NumericValueGenerator.get_taxonomy_non_eligible(relevant_pages, kpi, ai_model=ai_model)
    except ValueError:
        return create_not_attempted_report("Error retrieving prompted values for template 5")
    try:
        dataland_values = get_dataland_values(dataset, kpi)
    except RuntimeError:
        return create_not_attempted_report("Error retrieving dataland values for template 5")

    value, verdict, comment, quality = comparator.compare_non_eligible_values(prompted_values, dataland_values)
    if verdict == QaReportDataPointVerdict.QAACCEPTED:
        corrected_data = ExtendedDataPointNuclearAndGasNonEligible()
    else:
        corrected_data = ExtendedDataPointNuclearAndGasNonEligible(
            value=value,
            quality=quality,
            comment="",
            dataSource=get_data_source(dataset),
        )
    return QaReportDataPointExtendedDataPointNuclearAndGasNonEligible(
        comment=comment, verdict=verdict, correctedData=corrected_data
    )


def create_not_attempted_report(error_message: str) -> QaReportDataPointExtendedDataPointNuclearAndGasNonEligible:
    """Create a not attempted report frame for the Nuclear and Gas General Non Eligible."""
    return QaReportDataPointExtendedDataPointNuclearAndGasNonEligible(
        comment=error_message,
        verdict=QaReportDataPointVerdict.QANOTATTEMPTED,
        correctedData=ExtendedDataPointNuclearAndGasNonEligible(),
    )


def get_dataland_values(dataset: NuclearAndGasDataCollection, kpi: str) -> dict:
    """Retrieve dataland non_eligible values based on KPI."""
    try:
        if kpi == "Revenue":
            data = data_provider.get_taxonomy_non_eligible_revenue_values_by_data(dataset)
        else:
            data = data_provider.get_taxonomy_non_eligible_capex_values_by_data(dataset)
    except Exception as e:
        msg = f"Error retrieving dataland values for {kpi}: {e}"
        raise RuntimeError(msg) from e
    return data


def get_data_source(dataset: NuclearAndGasDataCollection) -> ExtendedDocumentReference | None:
    """Retrieve the data source mapped to a QA document reference."""
    data_sources = data_provider.get_datasources_of_nuclear_and_gas_numeric_values(data=dataset)
    data_source = data_sources.get("taxonomy_non_eligible")
    return comparator.map_doc_ref_to_qa_doc_ref(data_source)
