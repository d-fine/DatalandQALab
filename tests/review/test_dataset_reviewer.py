import unittest
from unittest.mock import patch

from dataland_qa_lab.review.dataset_reviewer import review_dataset


class TestReviewDataset(unittest.TestCase):
    def test_review_dataset_failure(self) -> None:
        with patch("dataland_qa_lab.dataland.dataset_provider.get_dataset_by_id", return_value=None):
            with self.assertRaises(RuntimeError) as cm:  # noqa: PT027
                review_dataset("invalid_data_id")
            assert "Error reviewing dataset" in str(cm.exception)
