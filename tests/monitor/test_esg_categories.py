"""Tests for ESG category support in the monitor."""

import pytest

from monitor.categories import ESGCategory, detect_category_from_dataset, get_category_config
from monitor.esg_monitor import ESGMonitor


@pytest.mark.parametrize("category", list(ESGCategory))
def test_monitor_supports_all_categories(category: ESGCategory) -> None:
    """Verify monitor can handle all ESG categories."""
    monitor = ESGMonitor(category)
    assert monitor.category == category
    assert monitor.config is not None
    assert hasattr(monitor.config, "id")
    assert hasattr(monitor.config, "display_name")
    assert hasattr(monitor.config, "dataset_type")


def test_category_detection_nuclear() -> None:
    """Test category detection for nuclear datasets."""
    dataset = {"metadata": {"type": "nuclear_facility"}, "data": {}}
    detected = detect_category_from_dataset(dataset)
    assert detected == ESGCategory.NUCLEAR


def test_category_detection_gas() -> None:
    """Test category detection for gas datasets."""
    dataset = {"metadata": {"type": "gas_infrastructure"}, "data": {}}
    detected = detect_category_from_dataset(dataset)
    assert detected == ESGCategory.GAS


def test_category_detection_renewable_energy() -> None:
    """Test category detection for renewable energy datasets."""
    dataset = {"data": {"renewable_energy": True, "general": {}}}
    detected = detect_category_from_dataset(dataset)
    assert detected == ESGCategory.RENEWABLE_ENERGY


def test_category_detection_fallback() -> None:
    """Test category detection falls back to NUCLEAR for unknown types."""
    dataset = {"metadata": {"type": "unknown_type"}, "data": {}}
    detected = detect_category_from_dataset(dataset)
    assert detected == ESGCategory.NUCLEAR


def test_category_detection_empty_dataset() -> None:
    """Test category detection with empty dataset returns None."""
    detected = detect_category_from_dataset({})
    assert detected is None


def test_category_detection_none_dataset() -> None:
    """Test category detection with None dataset returns None."""
    detected = detect_category_from_dataset(None)
    assert detected is None


def test_get_category_config_nuclear() -> None:
    """Test nuclear category configuration."""
    config = get_category_config(ESGCategory.NUCLEAR)
    assert config.id == "nuclear"
    assert config.display_name == "Nuclear Facilities"
    assert config.dataset_type == "nuclear_facility"
    assert "capacity" in config.required_fields


def test_get_category_config_gas() -> None:
    """Test gas category configuration."""
    config = get_category_config(ESGCategory.GAS)
    assert config.id == "gas"
    assert config.display_name == "Gas Infrastructure"
    assert "gas_type" in config.required_fields


def test_get_category_config_default() -> None:
    """Test default configuration for categories without specific config."""
    config = get_category_config(ESGCategory.CARBON_EMISSIONS)
    assert config.id == "carbon_emissions"
    assert "Carbon Emissions" in config.display_name
    assert config.dataset_type == "carbon_emissions"


def test_esg_monitor_validation_missing_required_field() -> None:
    """Test ESGMonitor detects missing required fields."""
    monitor = ESGMonitor(ESGCategory.NUCLEAR)
    dataset = {"name": "Test Facility"}  # Missing required fields like 'capacity', 'status', 'location'

    errors = monitor.validate(dataset)
    assert len(errors) > 0
    assert any("Missing required field" in error for error in errors)


def test_esg_monitor_validation_rule_violation() -> None:
    """Test ESGMonitor detects validation rule violations."""
    monitor = ESGMonitor(ESGCategory.NUCLEAR)
    dataset = {
        "facility_id": "test-1",
        "name": "Test",
        "capacity": -100,  # Below minimum
        "status": "active",
        "location": "Test Location",
    }

    errors = monitor.validate(dataset)
    assert any("below minimum" in error.lower() for error in errors)


def test_esg_monitor_validation_success() -> None:
    """Test ESGMonitor validation passes for valid dataset."""
    monitor = ESGMonitor(ESGCategory.NUCLEAR)
    dataset = {
        "facility_id": "test-1",
        "name": "Test Facility",
        "capacity": 1000,
        "status": "active",
        "location": "Test Location",
    }

    errors = monitor.validate(dataset)
    assert len(errors) == 0


@pytest.mark.parametrize(
    ("category", "expected_fields"),
    [
        (ESGCategory.NUCLEAR, ["capacity", "status", "location"]),
        (ESGCategory.GAS, ["gas_type", "volume", "operator"]),
        (ESGCategory.RENEWABLE_ENERGY, ["energy_type", "capacity", "co2_savings"]),
    ],
)
def test_category_required_fields(category: ESGCategory, expected_fields: list[str]) -> None:
    """Test that each category has the expected required fields."""
    config = get_category_config(category)
    for field in expected_fields:
        assert field in config.required_fields, f"Field '{field}' missing in {category.value} required_fields"
