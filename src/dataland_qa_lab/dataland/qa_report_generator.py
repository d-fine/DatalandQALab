# from dataland_qa_lab.dataland.yes_no_value_generator import YesNoValueGenerator


class QaReportGenerator:
    """A class to generate QA reports based on provided data and relevant pages."""
    def __init__(self, data_id: str, relevant_pages: bytes) -> None:
        """Initialize the QA report generator with data ID and relevant pages."""
        self.data_id: str = data_id
        self.relevant_pages: bytes = relevant_pages
        self.yes_no_values: list = []
        self.numeric_values: list[list] = [[]]
        self.report = None

    def get_yes_no_values(self) -> None:
        """Retrieve yes/no values for the QA report.

        To be implemented in subclasses YesNoValueGenerator.
        """

    def get_numeric_values(self) -> None:
        """Retrieve yes/no values for the QA report.

        To be implemented in subclasses NumericValueGenerator.
        """

    def build_qa_report(self) -> None:
        """Build the QA report from the provided data and relevant pages.

        To be implemented here.
        """
