from dataland_backend.models.extended_document_reference import (
    ExtendedDocumentReference as ExtendedDocumentReferenceBackend,
)
from dataland_qa.models.extended_document_reference import ExtendedDocumentReference


def map_doc_ref_to_qa_doc_ref(
    ref: ExtendedDocumentReferenceBackend | None
) -> ExtendedDocumentReference | None:
    """Map backend document reference to QA document reference."""
    if ref is None:
        return None

    return ExtendedDocumentReference(
        page=ref.page, fileName=ref.file_name, tagName=ref.tag_name, fileReference=ref.file_reference
    )
