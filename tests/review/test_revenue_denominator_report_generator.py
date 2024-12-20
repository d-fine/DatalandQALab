from unittest.mock import MagicMock

import pytest
from azure.ai.documentintelligence.models import AnalyzeResult

from dataland_qa_lab.dataland import data_provider
from dataland_qa_lab.review.numeric_value_generator import NumericValueGenerator
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
    NumericValueGenerator.get_taxonomy_alligned_denominator = MagicMock(return_value=[1, 2, 3, 4, 5, 6])


def test_compare_denominator_values() -> None:
    pass
