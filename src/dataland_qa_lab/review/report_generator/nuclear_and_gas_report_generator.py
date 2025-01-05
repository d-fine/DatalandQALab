from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_backend.models.extended_document_reference import (
    ExtendedDocumentReference as ExtendedDocumentReferenceBackend,
)
from dataland_qa.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_qa.models.extended_document_reference import ExtendedDocumentReference
from dataland_qa.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_qa.models.nuclear_and_gas_general import (
    NuclearAndGasGeneral,
)
from dataland_qa.models.nuclear_and_gas_general_general import NuclearAndGasGeneralGeneral
from dataland_qa.models.nuclear_and_gas_general_taxonomy_aligned_denominator import (
    NuclearAndGasGeneralTaxonomyAlignedDenominator,
)
from dataland_qa.models.nuclear_and_gas_general_taxonomy_aligned_numerator import (
    NuclearAndGasGeneralTaxonomyAlignedNumerator,
)
from dataland_qa.models.nuclear_and_gas_general_taxonomy_eligible_but_not_aligned import (
    NuclearAndGasGeneralTaxonomyEligibleButNotAligned,
)
from dataland_qa.models.nuclear_and_gas_general_taxonomy_non_eligible import (
    NuclearAndGasGeneralTaxonomyNonEligible,
)
from dataland_qa.models.qa_report_data_point_extended_data_point_yes_no import (
    QaReportDataPointExtendedDataPointYesNo,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review import yes_no_value_generator
from dataland_qa_lab.review.report_generator import (
    denominator_report_generator,
    eligible_not_aligned_report_generator,
    non_eligible_report_generator,
    numerator_report_generator,
)
from dataland_qa_lab.review.report_generator.abstract_report_generator import ReportGenerator
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


class NuclearAndGasReportGenerator(ReportGenerator):
    """Generate a quality assurance report."""

    relevant_pages: AnalyzeResult
    report: NuclearAndGasData

    def generate_report(self, relevant_pages: AnalyzeResult, dataset: NuclearAndGasDataCollection) -> NuclearAndGasData:
        """Assemble the QA Report based on the corrected values from Azure."""
        self.relevant_pages = relevant_pages

        self.report = self.build_report_frame()

        yes_no_data_points = self.compare_yes_no_values(dataset=dataset, relevant_pages=relevant_pages)
        for key, value in yes_no_data_points.items():
            setattr(self.report.general.general, key, value)

        self.report.general.taxonomy_aligned_denominator = (
            denominator_report_generator.build_taxonomy_aligned_denominator_report(
                dataset=dataset, relevant_pages=relevant_pages
            )
        )
        self.report.general.taxonomy_aligned_numerator = (
            numerator_report_generator.build_taxonomy_aligned_numerator_report(
                dataset=dataset, relevant_pages=relevant_pages
            )
        )
        self.report.general.taxonomy_eligible_but_not_aligned = (
            eligible_not_aligned_report_generator.build_taxonomy_eligible_but_not_aligned_report(
                dataset=dataset, relevant_pages=relevant_pages
            )
        )
        self.report.general.taxonomy_non_eligible = (
            non_eligible_report_generator.build_taxonomy_non_eligible_report(
                dataset=dataset, relevant_pages=relevant_pages
            )
        )

        return self.report

    @classmethod
    def build_report_frame(cls) -> NuclearAndGasData:
        """Create Report Frame."""
        report_frame = NuclearAndGasData(
            general=NuclearAndGasGeneral(
                general=NuclearAndGasGeneralGeneral(),
                taxonomyAlignedDenominator=NuclearAndGasGeneralTaxonomyAlignedDenominator(),
                taxonomyAlignedNumerator=NuclearAndGasGeneralTaxonomyAlignedNumerator(),
                taxonomyEligibleButNotAligned=NuclearAndGasGeneralTaxonomyEligibleButNotAligned(),
                taxonomyNonEligible=NuclearAndGasGeneralTaxonomyNonEligible(),
            )
        )

        return report_frame

    @classmethod
    def compare_yes_no_values(
        cls, dataset: NuclearAndGasDataCollection, relevant_pages: AnalyzeResult
    ) -> dict[str, QaReportDataPointExtendedDataPointYesNo | None]:
        """Build first yes no data point."""
        yes_no_values = yes_no_value_generator.get_yes_no_values_from_report(relevant_pages)
        yes_no_values_from_dataland = data_provider.get_yes_no_values_by_data(data=dataset)
        data_sources = data_provider.get_datasources_of_nuclear_and_gas_yes_no_questions(data=dataset)
        qa_data_points = {}

        for key, dataland_value in yes_no_values_from_dataland.items():
            corrected_value = yes_no_values.get(key)
            data_source = data_sources.get(key)

            if corrected_value != dataland_value:
                qa_data_points[key] = QaReportDataPointExtendedDataPointYesNo(
                    comment="tbd",
                    verdict=QaReportDataPointVerdict.QAREJECTED,
                    correctedData=ExtendedDataPointYesNo(
                        value=corrected_value,
                        quality="Incomplete",
                        comment="justification",
                        dataSource=cls.map_doc_ref_to_qa_doc_ref(data_source),
                    ),
                )
            else:
                qa_data_points[key] = QaReportDataPointExtendedDataPointYesNo(
                    comment="Geprüft durch AzureOpenAI",
                    verdict=QaReportDataPointVerdict.QAACCEPTED,
                    correctedData=ExtendedDataPointYesNo(),
                )

        return qa_data_points

    @classmethod
    def map_doc_ref_to_qa_doc_ref(
        cls, ref: ExtendedDocumentReferenceBackend | None
    ) -> ExtendedDocumentReference | None:
        """Mapper to convert backend doc ref to qa doc ref."""
        if ref is None:
            return None

        return ExtendedDocumentReference(
            page=ref.page, fileName=ref.file_name, tagName=ref.tag_name, fileReference=ref.file_reference
        )
