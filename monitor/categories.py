from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ESGCategory(str, Enum):
    """Enum representing ESG categories."""
    NUCLEAR = "nuclear"
    GAS = "gas"
    RENEWABLE_ENERGY = "renewable_energy"
    WATER_MANAGEMENT = "water_management"
    WASTE_MANAGEMENT = "waste_management"
    BIODIVERSITY = "biodiversity"
    CARBON_EMISSIONS = "carbon_emissions"
    SOCIAL_IMPACT = "social_impact"
    GOVERNANCE = "governance"


@dataclass
class CategoryConfig:
    """Configuration for a single ESG category dataset."""
    id: str
    display_name: str
    dataset_type: str
    key_fields: list[str]
    required_fields: list[str]
    validation_rules: dict = None

    def __post_init__(self) -> None:
        if self.validation_rules is None:
            self.validation_rules = {}


def detect_category_from_dataset(dataset: dict) -> ESGCategory | None:
    """Detect ESG category based on dataset content."""
    if not dataset:
        return None
    metadata_type = dataset.get("metadata", {}).get("type", "").lower()
    raw = str(dataset).lower()
    for category in ESGCategory:
        if category.value in metadata_type or category.value in raw:
            return category
    return ESGCategory.NUCLEAR


def get_category_config(category: ESGCategory) -> CategoryConfig:
    """Return the CategoryConfig for a given ESGCategory."""
    configs = {
        ESGCategory.NUCLEAR: CategoryConfig(
            id="nuclear",
            display_name="Nuclear Facilities",
            dataset_type="nuclear_facility",
            key_fields=["facility_id", "name"],
            required_fields=["capacity", "status", "location"],
            validation_rules={"capacity": {"min": 0, "max": 10000}}
        ),
        ESGCategory.GAS: CategoryConfig(
            id="gas",
            display_name="Gas Infrastructure",
            dataset_type="gas_infrastructure",
            key_fields=["facility_id", "name"],
            required_fields=["gas_type", "volume", "operator"],
            validation_rules={"volume": {"min": 0}}
        ),
        ESGCategory.RENEWABLE_ENERGY: CategoryConfig(
            id="renewable_energy",
            display_name="Renewable Energy Projects",
            dataset_type="renewable_energy",
            key_fields=["project_id", "name"],
            required_fields=["energy_type", "capacity", "co2_savings"],
            validation_rules={"capacity": {"min": 0}}
        ),
    }
    return configs.get(
        category,
        CategoryConfig(
            id=category.value,
            display_name=category.value.replace("_", " ").title(),
            dataset_type=category.value,
            key_fields=["id", "name"],
            required_fields=[],
            validation_rules={}
        )
    )
