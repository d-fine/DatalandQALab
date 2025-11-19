class ReportBuilder:
    def __init__(self):
        pass

    schema = {
        "data": {
            "general": {
                "general": {
                    "referencedReports": None,
                    "nuclearEnergyRelatedActivitiesSection426": {
                        "comment": "Reviewed by AzureOpenAI",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                    "nuclearEnergyRelatedActivitiesSection427": {
                        "comment": "Reviewed by AzureOpenAI",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                    "nuclearEnergyRelatedActivitiesSection428": {
                        "comment": "Reviewed by AzureOpenAI",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                    "fossilGasRelatedActivitiesSection429": {
                        "comment": "Reviewed by AzureOpenAI",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                    "fossilGasRelatedActivitiesSection430": {
                        "comment": "Reviewed by AzureOpenAI",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                    "fossilGasRelatedActivitiesSection431": {
                        "comment": "Reviewed by AzureOpenAI",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                },
                "taxonomyAlignedDenominator": {
                    "nuclearAndGasTaxonomyAlignedRevenueDenominator": {
                        "comment": "",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                    "nuclearAndGasTaxonomyAlignedCapexDenominator": {
                        "comment": "",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                },
                "taxonomyAlignedNumerator": {
                    "nuclearAndGasTaxonomyAlignedRevenueNumerator": {
                        "comment": "",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                    "nuclearAndGasTaxonomyAlignedCapexNumerator": {
                        "comment": "Discrepancy in 'taxonomy_aligned_share_numerator_n_and_g427': 0.21 != 0.0.Discrepancy in 'taxonomy_aligned_share_numerator_n_and_g427': 0.21 != 0.0.Discrepancy in 'taxonomy_aligned_share_numerator_n_and_g428': 1.3 != 0.0.Discrepancy in 'taxonomy_aligned_share_numerator_n_and_g428': 1.3 != 0.0.Discrepancy in 'taxonomy_aligned_share_numerator_n_and_g430': 0.01 != 0.0.Discrepancy in 'taxonomy_aligned_share_numerator_other_activities': 98.46 != 0.45.Discrepancy in 'taxonomy_aligned_share_numerator_other_activities': 98.44 != 0.45.Discrepancy in 'taxonomy_aligned_share_numerator_other_activities': 0.03 != 0.0.Discrepancy in 'taxonomy_aligned_share_numerator': 100 != 0.46.Discrepancy in 'taxonomy_aligned_share_numerator': 99.96 != 0.46.Discrepancy in 'taxonomy_aligned_share_numerator': 0.03 != 0.0.",
                        "verdict": "QaRejected",
                        "correctedData": {
                            "value": {
                                "taxonomyAlignedShareNumeratorNAndG426": {
                                    "mitigationAndAdaptation": 0,
                                    "mitigation": 0,
                                    "adaptation": 0,
                                },
                                "taxonomyAlignedShareNumeratorNAndG427": {
                                    "mitigationAndAdaptation": 0,
                                    "mitigation": 0,
                                    "adaptation": 0,
                                },
                                "taxonomyAlignedShareNumeratorNAndG428": {
                                    "mitigationAndAdaptation": 0,
                                    "mitigation": 0,
                                    "adaptation": 0,
                                },
                                "taxonomyAlignedShareNumeratorNAndG429": {
                                    "mitigationAndAdaptation": 0,
                                    "mitigation": 0,
                                    "adaptation": 0,
                                },
                                "taxonomyAlignedShareNumeratorNAndG430": {
                                    "mitigationAndAdaptation": 0,
                                    "mitigation": 0,
                                    "adaptation": 0,
                                },
                                "taxonomyAlignedShareNumeratorNAndG431": {
                                    "mitigationAndAdaptation": 0,
                                    "mitigation": 0,
                                    "adaptation": 0,
                                },
                                "taxonomyAlignedShareNumeratorOtherActivities": {
                                    "mitigationAndAdaptation": 0.45,
                                    "mitigation": 0.45,
                                    "adaptation": 0,
                                },
                                "taxonomyAlignedShareNumerator": {
                                    "mitigationAndAdaptation": 0.46,
                                    "mitigation": 0.46,
                                    "adaptation": 0,
                                },
                            },
                            "quality": "Reported",
                            "comment": "",
                            "dataSource": None,
                        },
                    },
                },
                "taxonomyEligibleButNotAligned": {
                    "nuclearAndGasTaxonomyEligibleButNotAlignedRevenue": {
                        "comment": "",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                    "nuclearAndGasTaxonomyEligibleButNotAlignedCapex": {
                        "comment": "",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                },
                "taxonomyNonEligible": {
                    "nuclearAndGasTaxonomyNonEligibleRevenue": {
                        "comment": "Discrepancy in 'taxonomy_non_eligible_share_other_activities': 60.55 != 39.0.Discrepancy in 'taxonomy_non_eligible_share': 60.55 != 39.0.",
                        "verdict": "QaRejected",
                        "correctedData": {
                            "value": {
                                "taxonomyNonEligibleShareNAndG426": 0,
                                "taxonomyNonEligibleShareNAndG427": 0,
                                "taxonomyNonEligibleShareNAndG428": 0,
                                "taxonomyNonEligibleShareNAndG429": 0,
                                "taxonomyNonEligibleShareNAndG430": 0,
                                "taxonomyNonEligibleShareNAndG431": 0,
                                "taxonomyNonEligibleShareOtherActivities": 39,
                                "taxonomyNonEligibleShare": 39,
                            },
                            "quality": "Reported",
                            "comment": "",
                            "dataSource": None,
                        },
                    },
                    "nuclearAndGasTaxonomyNonEligibleCapex": {
                        "comment": "",
                        "verdict": "QaAccepted",
                        "correctedData": {"value": None, "quality": None, "comment": None, "dataSource": None},
                    },
                },
            }
        }
    }
