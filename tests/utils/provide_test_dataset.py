from dataland_backend.models.extended_data_point_nuclear_and_gas_aligned_denominator import (
    ExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_backend.models.extended_data_point_nuclear_and_gas_aligned_numerator import (
    ExtendedDataPointNuclearAndGasAlignedNumerator,
)
from dataland_backend.models.extended_data_point_nuclear_and_gas_eligible_but_not_aligned import (
    ExtendedDataPointNuclearAndGasEligibleButNotAligned,
)
from dataland_backend.models.extended_data_point_nuclear_and_gas_non_eligible import (
    ExtendedDataPointNuclearAndGasNonEligible,
)
from dataland_backend.models.extended_data_point_yes_no import ExtendedDataPointYesNo
from dataland_backend.models.extended_document_reference import ExtendedDocumentReference
from dataland_backend.models.nuclear_and_gas_aligned_denominator import NuclearAndGasAlignedDenominator
from dataland_backend.models.nuclear_and_gas_aligned_numerator import NuclearAndGasAlignedNumerator
from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData
from dataland_backend.models.nuclear_and_gas_eligible_but_not_aligned import NuclearAndGasEligibleButNotAligned
from dataland_backend.models.nuclear_and_gas_environmental_objective import NuclearAndGasEnvironmentalObjective
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


def provide_test_dataset() -> NuclearAndGasData:
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
    datasource = ExtendedDocumentReference(
                    page="57",
                    fileName="2023_DNK_Concordia_Versicherungen",
                    fileReference="0a8eebb9e32d3c0a32a1083699352018afcbbe39458ab8441cd0c8985a466a59"
                )
    return NuclearAndGasGeneralGeneral(
        nuclearEnergyRelatedActivitiesSection426=ExtendedDataPointYesNo(
            value="No",
            quality="Audited",
            comment="",
            dataSource=datasource,
        ),
        nuclearEnergyRelatedActivitiesSection427=ExtendedDataPointYesNo(
            value="No",
            quality="Audited",
            comment="",
            dataSource=datasource,
        ),
        nuclearEnergyRelatedActivitiesSection428=ExtendedDataPointYesNo(
            value="No",
            quality="Audited",
            comment="",
            dataSource=datasource
        ),
        nuclearEnergyRelatedActivitiesSection429=ExtendedDataPointYesNo(
            value="Yes",
            quality="Audited",
            comment="",
            dataSource=datasource
        ),
        fossilGasRelatedActivitiesSection430=ExtendedDataPointYesNo(
            value="Yes",
            quality="Audited",
            comment="",
            dataSource=datasource
        ),
        fossilGasRelatedActivitiesSection431=ExtendedDataPointYesNo(
            value="No",
            quality="Audited",
            comment="",
            dataSource=datasource
        ),
    )


def create_template_2_reportframe() -> NuclearAndGasGeneralTaxonomyAlignedDenominator:
    return NuclearAndGasGeneralTaxonomyAlignedDenominator(
        nuclear_and_gas_taxonomy_aligned_revenue_denominator=ExtendedDataPointNuclearAndGasAlignedDenominator(
            value=NuclearAndGasAlignedDenominator(
                taxonomy_aligned_share_denominator_n_and_g429=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g430=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g431=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomyAlignedShareDenominatorOtherActivities=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.04, mitigation=0.03, adaptation=0.0
                ),
                taxonomyAlignedShareDenominator=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.04, mitigation=0.03, adaptation=0.0
                ),
            ),
            quality="Audited",
            comment="",
            datasource=ExtendedDocumentReference(
                            page="57",
                            fileName="2023_DNK_Concordia_Versicherungen",
                            fileReference="0a8eebb9e32d3c0a32a1083699352018afcbbe39458ab8441cd0c8985a466a59"
                        ),
        ),
        nuclearAndGasTaxonomyAlignedCapexDenominator=ExtendedDataPointNuclearAndGasAlignedDenominator(
            value=NuclearAndGasAlignedDenominator(
                taxonomy_aligned_share_denominator_n_and_g429=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g430=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g431=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomyAlignedShareDenominatorOtherActivities=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.07, mitigation=0.05, adaptation=0.0
                ),
                taxonomyAlignedShareDenominator=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.07, mitigation=0.05, adaptation=0.0
                ),
            ),
            quality="Audited",
            comment="",
            datasource=ExtendedDocumentReference(
                            page="60",
                            fileName="2023_DNK_Concordia_Versicherungen",
                            fileReference="0a8eebb9e32d3c0a32a1083699352018afcbbe39458ab8441cd0c8985a466a59"
                        ),
        )
    )


def create_template_3_reportframe() -> NuclearAndGasGeneralTaxonomyAlignedNumerator:
    return NuclearAndGasGeneralTaxonomyAlignedNumerator(
        nuclear_and_gas_taxonomy_aligned_revenue_numerator=ExtendedDataPointNuclearAndGasAlignedNumerator(
            value=NuclearAndGasAlignedNumerator(
                taxonomy_aligned_share_denominator_n_and_g429=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g430=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g431=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomyAlignedShareDenominatorOtherActivities=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=100.0, mitigation=84.84, adaptation=0.0
                ),
                taxonomyAlignedShareDenominator=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=100.0, mitigation=84.84, adaptation=0.0
                ),
            ),
            quality="Audited",
            comment="",
            datasource=ExtendedDocumentReference(
                            page="58",
                            fileName="2023_DNK_Concordia_Versicherungen",
                            fileReference="0a8eebb9e32d3c0a32a1083699352018afcbbe39458ab8441cd0c8985a466a59"
                        )
            ),
        nuclearAndGasTaxonomyAlignedCapexNumerator=ExtendedDataPointNuclearAndGasAlignedNumerator(
            value=NuclearAndGasAlignedNumerator(
                taxonomy_aligned_share_denominator_n_and_g429=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g430=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g431=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomyAlignedShareDenominatorOtherActivities=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=100.0, mitigation=81.57, adaptation=0.1
                ),
                taxonomyAlignedShareDenominator=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=100.0, mitigation=81.57, adaptation=0.1
                ),
            ),
            quality="Audited",
            comment="",
            datasource=ExtendedDocumentReference(
                            page="60",
                            fileName="2023_DNK_Concordia_Versicherungen",
                            fileReference="0a8eebb9e32d3c0a32a1083699352018afcbbe39458ab8441cd0c8985a466a59"
                        )
            ),
    )


def create_template_4_reportframe() -> NuclearAndGasGeneralTaxonomyEligibleButNotAligned:
    return NuclearAndGasGeneralTaxonomyEligibleButNotAligned(
        nuclear_and_gas_taxonomy_eligible_but_not_aligned_revenue=ExtendedDataPointNuclearAndGasEligibleButNotAligned(
            value=NuclearAndGasEligibleButNotAligned(
                taxonomy_aligned_share_denominator_n_and_g429=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g430=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g431=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomyAlignedShareDenominatorOtherActivities=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.26, mitigation=0.2, adaptation=0.0
                ),
                taxonomyAlignedShareDenominator=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.26, mitigation=0.2, adaptation=0.0
                ),
            ),
            quality="Audited",
            comment="",
            datasource=ExtendedDocumentReference(
                            page="58",
                            fileName="2023_DNK_Concordia_Versicherungen",
                            fileReference="0a8eebb9e32d3c0a32a1083699352018afcbbe39458ab8441cd0c8985a466a59"
                        )
        ),
        nuclearAndGasTaxonomyEligibleButNotAlignedCapex=ExtendedDataPointNuclearAndGasEligibleButNotAligned(
            value=NuclearAndGasEligibleButNotAligned(
                taxonomy_aligned_share_denominator_n_and_g429=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g430=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomy_aligned_share_denominator_n_and_g431=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.0, mitigation=0.0, adaptation=0.0
                ),
                taxonomyAlignedShareDenominatorOtherActivities=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.28, mitigation=0.18, adaptation=0.16
                ),
                taxonomyAlignedShareDenominator=NuclearAndGasEnvironmentalObjective(
                    mitigationAndAdaptation=0.28, mitigation=0.18, adaptation=0.16
                ),
            ),
            quality="Audited",
            comment="",
            datasource=ExtendedDocumentReference(
                            page="60-61",
                            fileName="2023_DNK_Concordia_Versicherungen",
                            fileReference="0a8eebb9e32d3c0a32a1083699352018afcbbe39458ab8441cd0c8985a466a59"
                        )
        ),
    )


def create_template_5_reportframe() -> NuclearAndGasGeneralTaxonomyNonEligible:
    return NuclearAndGasGeneralTaxonomyNonEligible(
        nuclear_and_gas_taxonomy_non_eligible_revenue=ExtendedDataPointNuclearAndGasNonEligible(

            value=NuclearAndGasNonEligible(
                taxonomy_non_eligible_share=0.65,
            ),
            quality="Audited",
            comment="",
            datasource=ExtendedDocumentReference(
                            page="58-59",
                            fileName="2023_DNK_Concordia_Versicherungen",
                            fileReference="0a8eebb9e32d3c0a32a1083699352018afcbbe39458ab8441cd0c8985a466a59"
                        )
        ),
        nuclearAndGasTaxonomyNonEligibleCapex=ExtendedDataPointNuclearAndGasNonEligible(
            value=NuclearAndGasNonEligible(
                taxonomy_non_eligible_share=0.6,
            ),
            quality="Audited",
            comment="",
            datasource=ExtendedDocumentReference(
                            page="61",
                            fileName="2023_DNK_Concordia_Versicherungen",
                            fileReference="0a8eebb9e32d3c0a32a1083699352018afcbbe39458ab8441cd0c8985a466a59"
                        )
        )
    )
