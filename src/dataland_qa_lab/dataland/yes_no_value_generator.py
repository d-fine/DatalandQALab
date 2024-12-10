# import Promting Service
class YesNoValueGenerator:
    """A class to generate yes/no values for QA reports."""
    def __init__(self) -> None:
        """Initialize the yes/no value generator with data ID and relevant pages."""
        self.yes_no_values: list = []

    def build_prompt(self) -> None:
        """Call the Promting Service to build Prompt.

        To be implemented in subclasses YesNoValueGenerator.
        """

    def get_correct_values_from_report(self) -> None:
        """Retrieve correct values from the report.

        To be implemented here.
        """

    def compare_values(self) -> None:
        """Compare values from the report.

        To be implemented here.
        """
