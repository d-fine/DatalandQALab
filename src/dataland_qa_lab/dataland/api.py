import io
import json

import pypdf
import requests
from attr import dataclass

from dataland_qa_lab.utils.config import get_config

conf = get_config()

headers = {
    "Authorization": "Bearer " + conf.dataland_api_key,
    "accept": "application/json",
}


@dataclass
class QaStatus:
    """QA status options."""

    Accepted = "Accepted"
    Rejected = "Rejected"
    Pending = "Pending"


def get_data_point(data_point_id: str) -> dict:
    """Get document details from Dataland."""
    url = f"{conf.dataland_url}/api/data-points/{data_point_id}"
    res = requests.request("GET", url, headers=headers)

    if res.status_code == requests.codes.ok:
        res = res.json()
        res["dataPoint"] = json.loads(res["dataPoint"])
        return res
    return {}


def get_document(file_reference: str, page_numbers: list[int]) -> pypdf.PdfReader:
    """Get a document from dataland by its file reference and extract relevant pages."""
    full_pdf = conf.dataland_client.documents_api.get_document(file_reference)
    full_pdf_stream = io.BytesIO(full_pdf)

    original_pdf = pypdf.PdfReader(full_pdf_stream)
    output_pdf = pypdf.PdfWriter()

    for page_num in page_numbers:
        if 0 <= page_num - 1 < len(original_pdf.pages):
            output_pdf.add_page(original_pdf.pages[page_num - 1])

    extracted_pdf_stream = io.BytesIO()
    output_pdf.write(extracted_pdf_stream)
    extracted_pdf_stream.seek(0)

    return extracted_pdf_stream


def update_data_point_qa_report(data_point_id: str, qa_status: str, comment: str) -> None:
    """Post data point QA report to Dataland."""
    url = f"{conf.dataland_url}/qa/data-points/{data_point_id}?qaStatus={qa_status!s}&comment={comment}"

    requests.request(
        "POST",
        url,
        headers=headers,
    )
