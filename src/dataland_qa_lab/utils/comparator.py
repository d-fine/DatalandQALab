from dataland_backend.models.extended_document_reference import (
    ExtendedDocumentReference as ExtendedDocumentReferenceBackend,
)
from dataland_qa.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_qa.models.extended_document_reference import ExtendedDocumentReference
from dataland_qa.models.nuclear_and_gas_environmental_objective import NuclearAndGasEnvironmentalObjective
from dataland_qa.models.nuclear_and_gas_non_eligible import NuclearAndGasNonEligible
from dataland_qa.models.qa_report_data_point_extended_data_point_yes_no import (
    QaReportDataPointExtendedDataPointYesNo,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict


def compare_yes_no_values(
    yes_no_values: list, yes_no_values_from_dataland: dict, data_sources: dict
) -> dict[str, QaReportDataPointExtendedDataPointYesNo | None]:
    """Build first yes no data point."""
    qa_data_points = {}

    for field_name, dataland_value in yes_no_values_from_dataland.items():
        corrected_value = yes_no_values.get(field_name)
        data_source = data_sources.get(field_name)

        if corrected_value != dataland_value:
            qa_data_points[field_name] = QaReportDataPointExtendedDataPointYesNo(
                comment=(f"Discrepancy in '{field_name}': {dataland_value} != {corrected_value}."),
                verdict=QaReportDataPointVerdict.QAREJECTED,
                correctedData=ExtendedDataPointYesNo(
                    value=corrected_value,
                    quality="Reported",
                    comment="",
                    dataSource=map_doc_ref_to_qa_doc_ref(data_source),
                ),
            )
        else:
            qa_data_points[field_name] = QaReportDataPointExtendedDataPointYesNo(
                comment="Reviewed by AzureOpenAI.",
                verdict=QaReportDataPointVerdict.QAACCEPTED,
                correctedData=ExtendedDataPointYesNo(),
            )

    return qa_data_points


def compare_values_template_2to4(
    prompted_values: list, dataland_values: dict, obj_class: any
) -> tuple[any, QaReportDataPointVerdict, str, str]:
    """Generalized value comparison function."""
    chunked_prompt_vals = [prompted_values[i : i + 3] for i in range(0, len(prompted_values), 3)]
    corrected_values = obj_class()
    verdict = QaReportDataPointVerdict.QAACCEPTED
    quality = "Reported"
    comments = []

    for (field_name, dataland_vals), prompt_vals in zip(dataland_values.items(), chunked_prompt_vals, strict=False):
        for prompt_val, dataland_val in zip(prompt_vals, dataland_vals, strict=False):
            if prompt_val == -1 and dataland_val != -1:
                quality = "NoDataFound"
                verdict = QaReportDataPointVerdict.QAREJECTED
                comments.append(f"No Data found for '{field_name}': {dataland_val} != {prompt_val}.")
            elif prompt_val != dataland_val:
                verdict = QaReportDataPointVerdict.QAREJECTED
                comments.append(f"Discrepancy in '{field_name}': {dataland_val} != {prompt_val}.")
        update_attribute(corrected_values, field_name, prompt_vals)

    return corrected_values, verdict, "".join(comments), quality


def compare_non_eligible_values(
    prompted_values: list, dataland_values: dict
) -> tuple[NuclearAndGasNonEligible, QaReportDataPointVerdict, str, str]:
    """Compare non_eligible_values values and return results."""
    value = NuclearAndGasNonEligible()
    verdict = QaReportDataPointVerdict.QAACCEPTED
    quality = "Reported"
    comment = ""
    for index, (field_name, dataland_value) in enumerate(dataland_values.items()):
        prompt_value = prompted_values[index]
        if prompt_value == -1 and dataland_value != -1:
            quality = "NoDataFound"
            verdict = QaReportDataPointVerdict.QAREJECTED
            comment += f"No Data found for'{field_name}': {dataland_value} != {prompt_value}."
        elif dataland_value != prompt_value:
            verdict = QaReportDataPointVerdict.QAREJECTED
            comment += f"Discrepancy in '{field_name}': {dataland_value} != {prompt_value}."
        update_attribute(value, field_name, prompt_value)

    return value, verdict, comment, quality


def update_attribute(obj: any, attribute_name: str, attribute_value: list | float) -> None:
    """Set an attribute of the object by its name, handling specific cases for different object types."""
    if obj.__class__.__name__ == "NuclearAndGasNonEligible":
        attribute_value = -1 if attribute_value is None else attribute_value
        setattr(obj, attribute_name, attribute_value)
    else:
        processed_values = [None if v == -1 else v for v in attribute_value]
        setattr(
            obj,
            attribute_name,
            NuclearAndGasEnvironmentalObjective(
                mitigationAndAdaptation=processed_values[0],
                mitigation=processed_values[1],
                adaptation=processed_values[2],
            ),
        )


def map_doc_ref_to_qa_doc_ref(ref: ExtendedDocumentReferenceBackend | None) -> ExtendedDocumentReference | None:
    """Map backend document reference to QA document reference."""
    if ref is None:
        return None

    return ExtendedDocumentReference(
        page=ref.page, fileName=ref.file_name, tagName=ref.tag_name, fileReference=ref.file_reference
    )
