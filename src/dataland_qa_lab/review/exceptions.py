class ReviewError(Exception):
    """Base exception for errors during the review process."""


class DatasetNotFoundError(ReviewError):
    """Raised when a dataset with the given data_id cannot be found."""


class DataCollectionError(ReviewError):
    """Raised when the data collection cannot be created from dataset.data."""


class OCRProcessingError(ReviewError):
    """Raised when OCR or text extraction fails."""


class ReportSubmissionError(ReviewError):
    """Raised when posting the QA report to Dataland fails."""
