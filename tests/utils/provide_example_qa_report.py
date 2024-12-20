from dataland_backend.models.extended_data_point_nuclear_and_gas_aligned_denominator import (
    ExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_backend.models.extended_data_point_nuclear_and_gas_aligned_numerator import (
    ExtendedDataPointNuclearAndGasAlignedNumerator,
)
from dataland_backend.models.extended_data_point_nuclear_and_gas_non_eligible import (
    ExtendedDataPointNuclearAndGasNonEligible,
)
from dataland_backend.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
from dataland_backend.models.nuclear_and_gas_aligned_numerator import NuclearAndGasAlignedNumerator
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_backend.models.nuclear_and_gas_eligible_but_not_aligned import NuclearAndGasEligibleButNotAligned
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
from dataland_backend.models.nuclear_and_gas_non_eligible import NuclearAndGasNonEligible
from dataland_qa.models.nuclear_and_gas_aligned_denominator import NuclearAndGasAlignedDenominator
from dataland_qa.models.nuclear_and_gas_environmental_objective import NuclearAndGasEnvironmentalObjective
from dataland_qa.models.qa_report_data_point_extended_data_point_nuclear_and_gas_aligned_denominator import (
    QaReportDataPointExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_qa.models.qa_report_data_point_extended_data_point_nuclear_and_gas_aligned_numerator import (
    QaReportDataPointExtendedDataPointNuclearAndGasAlignedNumerator,
)
from dataland_qa.models.qa_report_data_point_extended_data_point_nuclear_and_gas_eligible_but_not_aligned import (
    QaReportDataPointExtendedDataPointNuclearAndGasEligibleButNotAligned,
)
from dataland_qa.models.qa_report_data_point_extended_data_point_nuclear_and_gas_non_eligible import (
    QaReportDataPointExtendedDataPointNuclearAndGasNonEligible,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict


def provide_example_qa_report() -> NuclearAndGasData:
    """Create Report Frame."""
    report_frame = NuclearAndGasData(
        general=NuclearAndGasGeneral(
            general=create_template_1_reportframe(),
            taxonomyAlignedDenominator=create_template_2_reportframe(),
            taxonomyAlignedNumerator=create_template_3_reportframe(),
            taxonomyEligibleButNotAligned=create_template_4_reportframe(),
            taxonomyNonEligible=create_template_5_reportframe(),
        )
    )

    return report_frame


def create_template_1_reportframe() -> NuclearAndGasGeneralGeneral:
    return NuclearAndGasGeneralGeneral(
        nuclearEnergyRelatedActivitiesSection426=ExtendedDataPointYesNo(
            value="No",
            quality="Audited",
            comment="",
            dataSource=ExtendedDocumentReference(
                page="57", fileName="2023_DNK_Concordia_Versicherungen", fileReference="1234"
            ),
        ),
        nuclearEnergyRelatedActivitiesSection427=ExtendedDataPointYesNo(
            value="No",
            quality="Audited",
            comment="",
            dataSource=ExtendedDocumentReference(
                page="57", fileName="2023_DNK_Concordia_Versicherungen", fileReference="1234"
            ),
        ),
        nuclearEnergyRelatedActivitiesSection428=ExtendedDataPointYesNo(
            value="No",
            quality="Audited",
            comment="",
            dataSource=ExtendedDocumentReference(
                page="57", fileName="2023_DNK_Concordia_Versicherungen", fileReference="1234"
            ),
        ),
        nuclearEnergyRelatedActivitiesSection429=ExtendedDataPointYesNo(
            value="Yes",
            quality="Audited",
            comment="",
            dataSource=ExtendedDocumentReference(
                page="57", fileName="2023_DNK_Concordia_Versicherungen", fileReference="1234"
            ),
        ),
        fossilGasRelatedActivitiesSection430=ExtendedDataPointYesNo(
            value="Yes",
            quality="Audited",
            comment="",
            dataSource=ExtendedDocumentReference(
                page="57", fileName="2023_DNK_Concordia_Versicherungen", fileReference="1234"
            ),
        ),
        fossilGasRelatedActivitiesSection431=ExtendedDataPointYesNo(
            value="Yes",
            quality="Audited",
            comment="",
            dataSource=ExtendedDocumentReference(
                page="57", fileName="2023_DNK_Concordia_Versicherungen", fileReference="1234"
            ),
        ),
    )


def create_template_2_reportframe() -> NuclearAndGasGeneralTaxonomyAlignedDenominator:
    return NuclearAndGasGeneralTaxonomyAlignedDenominator(
        nuclear_and_gas_taxonomy_aligned_revenue_denominator=QaReportDataPointExtendedDataPointNuclearAndGasAlignedDenominator(
            comment="",
            verdict=QaReportDataPointVerdict.QAACCEPTED,
            correctedData=ExtendedDataPointNuclearAndGasAlignedDenominator(
                value=NuclearAndGasAlignedDenominator(
                    taxonomy_aligned_share_denominator_n_and_g426=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomy_aligned_share_denominator_n_and_g427=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomy_aligned_share_denominator_n_and_g428=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomy_aligned_share_denominator_n_and_g429=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomy_aligned_share_denominator_n_and_g430=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomy_aligned_share_denominator_n_and_g431=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomyAlignedShareDenominatorOtherActivities=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0.04", mitigation="0.03", adaptation="0"
                    ),
                    taxonomyAlignedShareDenominator=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0.04", mitigation="0.03", adaptation="0"
                    ),
                ),
                quality="Audited",
                comment="",
                dataSource=ExtendedDocumentReference(
                    page="57", fileName="2023_DNK_Concordia_Versicherungen", fileReference="1234"
                ),
            ),
        )
    )


def create_template_3_reportframe() -> NuclearAndGasGeneralTaxonomyAlignedNumerator:
    return NuclearAndGasGeneralTaxonomyAlignedNumerator(
        nuclear_and_gas_taxonomy_aligned_revenue_numerator=QaReportDataPointExtendedDataPointNuclearAndGasAlignedNumerator(
            comment="",
            verdict=QaReportDataPointVerdict.QAACCEPTED,
            correctedData=ExtendedDataPointNuclearAndGasAlignedNumerator(
                value=NuclearAndGasAlignedNumerator(
                    taxonomy_aligned_share_denominator_n_and_g426=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomy_aligned_share_denominator_n_and_g427=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomy_aligned_share_denominator_n_and_g428=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomy_aligned_share_denominator_n_and_g429=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomy_aligned_share_denominator_n_and_g430=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomy_aligned_share_denominator_n_and_g431=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                    ),
                    taxonomyAlignedShareDenominatorOtherActivities=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="100", mitigation="84.84", adaptation="0"
                    ),
                    taxonomyAlignedShareDenominator=NuclearAndGasEnvironmentalObjective(
                        mitigationAndAdaptation="100", mitigation="84.84", adaptation="0"
                    ),
                ),
                quality="Audited",
                comment="",
                dataSource=ExtendedDocumentReference(
                    page="58", fileName="2023_DNK_Concordia_Versicherungen", fileReference="1234"
                ),
            ),
        )
    )


def create_template_4_reportframe() -> NuclearAndGasGeneralTaxonomyEligibleButNotAligned:
    return NuclearAndGasGeneralTaxonomyEligibleButNotAligned(
        nuclear_and_gas_taxonomy_eligible_but_not_aligned_revenue=QaReportDataPointExtendedDataPointNuclearAndGasEligibleButNotAligned(
            value=NuclearAndGasEligibleButNotAligned(
                taxonomy_aligned_share_denominator_n_and_g426=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                ),
                taxonomy_aligned_share_denominator_n_and_g427=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                ),
                taxonomy_aligned_share_denominator_n_and_g428=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                ),
                taxonomy_aligned_share_denominator_n_and_g429=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                ),
                taxonomy_aligned_share_denominator_n_and_g430=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                ),
                taxonomy_aligned_share_denominator_n_and_g431=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation="0", mitigation="0", adaptation="0"
                ),
                taxonomyAlignedShareDenominatorOtherActivities=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation="0.26", mitigation="0.2", adaptation="0"
                ),
                taxonomyAlignedShareDenominator=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation="0.26", mitigation="0.3", adaptation="0"
                ),
            ),
            quality="Audited",
            comment="",
            dataSource=ExtendedDocumentReference(
                page="58", fileName="2023_DNK_Concordia_Versicherungen", fileReference="1234"
            ),
        )
    )


def create_template_5_reportframe() -> NuclearAndGasGeneralTaxonomyNonEligible:
    return NuclearAndGasGeneralTaxonomyNonEligible(
        nuclear_and_gas_taxonomy_non_eligible_revenue=QaReportDataPointExtendedDataPointNuclearAndGasNonEligible(
            comment="",
            verdict=QaReportDataPointVerdict.QAACCEPTED,
            correctedData=ExtendedDataPointNuclearAndGasNonEligible(
                value=NuclearAndGasNonEligible(
                    taxonomy_non_eligible_share_n_and_g426=0.0,
                    taxonomy_non_eligible_share_n_and_g427=0.0,
                    taxonomy_non_eligible_share_n_and_g428=0.0,
                    taxonomy_non_eligible_share_n_and_g429=0.0,
                    taxonomy_non_eligible_share_n_and_g430=0.0,
                    taxonomy_non_eligible_share_n_and_g431=0.0,
                    taxonomy_non_eligible_share_other_activities=0.0,
                    taxonomy_non_eligible_share=0.65,
                ),
                quality="Audited",
                comment="",
                dataSource=ExtendedDocumentReference(
                    page="58-59", fileName="2023_DNK_Concordia_Versicherungen", fileReference="1234"
                ),
            ),
        )
    )
