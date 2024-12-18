from unittest.mock import MagicMock

import pytest
from azure.ai.documentintelligence.models import AnalyzeResult
from dataland_qa.models.extended_data_point_nuclear_and_gas_aligned_denominator import (
    ExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_qa.models.nuclear_and_gas_aligned_denominator import NuclearAndGasAlignedDenominator
from dataland_qa.models.qa_report_data_point_extended_data_point_nuclear_and_gas_aligned_denominator import (
    QaReportDataPointExtendedDataPointNuclearAndGasAlignedDenominator,
)
from dataland_qa.models.qa_report_data_point_verdict import QaReportDataPointVerdict

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review.numeric_value_generator import NumericValueGenerator
from dataland_qa_lab.review.report_generator.revenue_denominator_report_generator import (
    build_report,
    compare_denominator_values,
    get_data_source,
)
from dataland_qa_lab.utils.nuclear_and_gas_data_collection import NuclearAndGasDataCollection


@pytest.fixture
def mock_dataset() -> NuclearAndGasDataCollection:
    # Create a mock or dummy dataset as required by NuclearAndGasDataCollection
    dummy_dataset = MagicMock()
    dataset = NuclearAndGasDataCollection(dummy_dataset)
    return dataset


@pytest.fixture
def mock_relevant_pages() -> MagicMock:
    return MagicMock(spec=AnalyzeResult)


@pytest.fixture
def mock_data_provider() -> None:
    data_provider.get_taxonomy_aligned_denominator_values_by_data = MagicMock(
        return_value={
            "field_1": [1, 2, 3],
            "field_2": [4, 5, 6],
        }
    )
    data_provider.get_datasources_of_nuclear_and_gas_numeric_values = MagicMock(
        return_value={"taxonomy_aligned_denominator": MagicMock()}
    )


@pytest.fixture
def mock_numeric_value_generator() -> None:
    NumericValueGenerator.get_taxonomy_alligned_denominator = MagicMock(
        return_value=[1, 2, 3, 4, 5, 6]
    )


def test_compare_denominator_values(mock_dataset, mock_relevant_pages, mock_data_provider, mock_numeric_value_generator) -> None:
    aligned_denominator, verdict, comment = compare_denominator_values(
        mock_dataset, mock_relevant_pages
    )

    assert isinstance(aligned_denominator, NuclearAndGasAlignedDenominator)
    assert verdict == QaReportDataPointVerdict.QAACCEPTED
    assert comment == ""


def test_compare_denominator_values_with_discrepancy(
    mock_dataset, mock_relevant_pages, mock_data_provider, mock_numeric_value_generator
) -> None:
    # Modify the mock to create a discrepancy
    mock_data_provider()
    mock_numeric_value_generator()
    NumericValueGenerator.get_taxonomy_alligned_denominator.return_value = [1, 2, 3, 7, 8, 9]

    _aligned_denominator, verdict, comment = compare_denominator_values(
        mock_dataset, mock_relevant_pages
    )

    assert verdict == QaReportDataPointVerdict.QAREJECTED
    assert "Discrepancy" in comment


def test_get_data_source(mock_dataset, mock_data_provider) -> None:
    data_source = get_data_source(mock_dataset)

    assert data_source is not None


def test_build_report(mock_dataset, mock_relevant_pages, mock_data_provider, mock_numeric_value_generator) -> None:
    report = build_report(mock_dataset, mock_relevant_pages)

    assert isinstance(
        report, QaReportDataPointExtendedDataPointNuclearAndGasAlignedDenominator
    )
    assert isinstance(report.correctedData, ExtendedDataPointNuclearAndGasAlignedDenominator)
    assert report.verdict == QaReportDataPointVerdict.QAACCEPTED
