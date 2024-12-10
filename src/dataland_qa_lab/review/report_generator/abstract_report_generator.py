from abc import ABC, abstractmethod

from azure.ai.documentintelligence.models import AnalyzeResult


class ReportGenerator(ABC):
    """Abstract interfaces for report generators for different frameworks."""

    @abstractmethod
    def generate_report(self, relevant_pages: AnalyzeResult, dataset: any) -> any:
        """Generate a QA Report for any framework."""

    @abstractmethod
    def build_report_frame(self) -> any:
        """Create a dataless frame."""
