from dataland_backend.models.nuclear_and_gas_data import NuclearAndGasData

from dataland_qa_lab.models.datapoint_classes import (
    TaxonomyAlignedNumeratorDatapoint,
    TaxonomyEligibleButNotAlignedDatapoint,
    TaxonomyNonEligibleDatapoint,
    TaxononmyAlignedDenominatorDatapoint,
    YesNoDatapoint,
)


class NuclearAndGasDataCollection:
    """Class to bundle data regarding a dataset of nuclear and gas."""

    dataset: NuclearAndGasData
    yes_no_data_points: dict[str, YesNoDatapoint | None]
    taxonomy_aligned_denominator: dict[str, TaxononmyAlignedDenominatorDatapoint | None]
    taxonomy_aligned_numerator: dict[str, TaxonomyAlignedNumeratorDatapoint | None]
    taxonomy_eligble_but_not_aligned: dict[str, TaxonomyEligibleButNotAlignedDatapoint | None]
    taxonomy_non_eligible: dict[str, TaxonomyNonEligibleDatapoint | None]

    def __init__(self, dataset: NuclearAndGasData) -> None:
        """Intialize class."""
        self.dataset = dataset
        self.map_dataset_to_yes_no_dict()
        self.map_dataset_to_numeric_dict()

    def map_dataset_to_yes_no_dict(self) -> dict[str, YesNoDatapoint | None]:
        """Mapper function."""
        data = self.dataset.general.general

        self.yes_no_data_points = {
            "nuclear_energy_related_activities_section426": YesNoDatapoint(
                datapoint=data.nuclear_energy_related_activities_section426,
            ),
            "nuclear_energy_related_activities_section427": YesNoDatapoint(
                datapoint=data.nuclear_energy_related_activities_section427,
            ),
            "nuclear_energy_related_activities_section428": YesNoDatapoint(
                datapoint=data.nuclear_energy_related_activities_section428,
            ),
            "fossil_gas_related_activities_section429": YesNoDatapoint(
                datapoint=data.fossil_gas_related_activities_section429
            ),
            "fossil_gas_related_activities_section430": YesNoDatapoint(
                datapoint=data.fossil_gas_related_activities_section430
            ),
            "fossil_gas_related_activities_section431": YesNoDatapoint(
                datapoint=data.fossil_gas_related_activities_section431
            ),
        }

    def map_dataset_to_numeric_dict(self) -> None:
        """Mapper function."""
        data = self.dataset.general

        self.taxonomy_aligned_denominator = {
            "taxonomy_aligned_capex_denominator": TaxononmyAlignedDenominatorDatapoint(
                data.taxonomy_aligned_denominator.nuclear_and_gas_taxonomy_aligned_capex_denominator
            ),
            "taxonomy_aligned_revenue_denominator": TaxononmyAlignedDenominatorDatapoint(
                data.taxonomy_aligned_denominator.nuclear_and_gas_taxonomy_aligned_revenue_denominator
            ),
        }

        self.taxonomy_aligned_numerator = {
            "taxonomy_aligned_capex_numerator": TaxonomyAlignedNumeratorDatapoint(
                data.taxonomy_aligned_numerator.nuclear_and_gas_taxonomy_aligned_capex_numerator
            ),
            "taxonomy_aligned_revenue_numerator": TaxonomyAlignedNumeratorDatapoint(
                data.taxonomy_aligned_numerator.nuclear_and_gas_taxonomy_aligned_revenue_numerator
            ),
        }

        self.taxonomy_eligble_but_not_aligned = {
            "taxonomy_not_aligned_capex": TaxonomyEligibleButNotAlignedDatapoint(
                data.taxonomy_eligible_but_not_aligned.nuclear_and_gas_taxonomy_eligible_but_not_aligned_capex
            ),
            "taxonomy_not_aligned_revenue": TaxonomyEligibleButNotAlignedDatapoint(
                data.taxonomy_eligible_but_not_aligned.nuclear_and_gas_taxonomy_eligible_but_not_aligned_revenue
            ),
        }

        self.taxonomy_non_eligible = {
            "taxonomy_non_eligible_capex": TaxonomyNonEligibleDatapoint(
                data.taxonomy_non_eligible.nuclear_and_gas_taxonomy_non_eligible_capex
            ),
            "taxonomy_non_eligible_revenue": TaxonomyNonEligibleDatapoint(
                data.taxonomy_non_eligible.nuclear_and_gas_taxonomy_non_eligible_revenue
            ),
        }