import io

import pypdf
import requests

from dataland_qa_lab.utils.config import get_config

conf = get_config()

headers = {
    "Authorization": "Bearer " + conf.dataland_api_key,
    "accept": "application/json",
}


def get_data_point(data_point_id: str) -> dict | None:
    """Get document details from Dataland."""
    url = f"{conf.dataland_url}/api/data-points/{data_point_id}"
    res = requests.request("GET", url, headers=headers)

    if res.status_code == requests.codes.ok:
        return res.json()
    return None


def get_document(document_id: str):
    full_pdf = conf.dataland_client.documents_api.get_document(document_id)
    full_pdf_stream = io.BytesIO(full_pdf)

    original_pdf = pypdf.PdfReader(full_pdf_stream)
    output_pdf = pypdf.PdfWriter()

def post_data_point_qwa_report(data_point_id:str, qa_report:dict):
    # todo: implement