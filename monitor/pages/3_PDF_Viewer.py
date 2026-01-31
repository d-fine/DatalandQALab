# noqa: N999
from io import BytesIO

import requests
import streamlit as st

from utils import dataland


def _render_pdf(reference_id: str) -> None:
    try:
        response = dataland.download_document(reference_id)
        pdf_bytes = response.content
        buffer = BytesIO(pdf_bytes)
        st.download_button("View PDF in browser", buffer, file_name="document.pdf", mime="application/pdf")
    except requests.RequestException as error:
        st.error(f"❌ Failed to download PDF: {error}")


def render_pdf_viewer() -> None:
    """Render the PDF viewer page."""
    st.title("PDF Viewer")

    params = st.query_params
    reference_id = params.get("reference_id")

    if not reference_id:
        st.info("Click a PDF link on the analytics tab to view the referenced PDF document here.")
        return

    _render_pdf(reference_id)


render_pdf_viewer()
