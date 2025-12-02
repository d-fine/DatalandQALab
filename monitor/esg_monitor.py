from monitor.categories import ESGCategory, get_category_config


class ESGMonitor:
    """Performs validation of datasets based on category-specific rules.

    The fetching is still handled by main.py calling get_dataset_by_id().
    """

    def __init__(self, category: ESGCategory) -> None:
        """Initialize the monitor with a specific category."""
        self.category = category
        self.config = get_category_config(category)

    def validate(self, source_of_truth: dict) -> list[str]:
        """Validate dataset fields based on the category's configuration.

        Returns a list of validation error messages.
        """
        errors = [
            f"Missing required field: '{field}'"
            for field in self.config.required_fields
            if field not in source_of_truth
        ]

        for field, rules in self.config.validation_rules.items():
            if field in source_of_truth:
                value = source_of_truth[field]
                if "min" in rules and value < rules["min"]:
                    errors.append(f"Field '{field}' below minimum ({value} < {rules['min']})")
                if "max" in rules and value > rules["max"]:
                    errors.append(f"Field '{field}' above maximum ({value} > {rules['max']})")

        return errors
