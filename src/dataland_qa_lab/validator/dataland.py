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

def post_data_point_qa_report(data_point_id:str, qa_report:dict) -> dict | None:
    """Post data point QA report to Dataland."""
    url = f"{conf.dataland_url}/api/data-points/{data_point_id}/qa-reports"
    
    res = requests.request(
        "POST",
        url,
        headers=headers,
        json=qa_report,
    )
    
    #res.ok würde 201, 202 etc. auch abdecken
    if res.status_code == requests.codes.ok:
        return res.json()
    
    print(f"Error sending report: {res.status_code} - {res.text}")
    return None
    