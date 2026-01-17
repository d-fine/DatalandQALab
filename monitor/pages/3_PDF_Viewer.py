import tempfile  # noqa: N999

import Path
import streamlit as st
from utils import dataland

st.title("PDF Viewer")

params = st.query_params
reference_id = params.get("reference_id")

if not reference_id:
    st.info("Click a PDF link on the analytics tab to view the referenced PDF document here.")
else:
    # Download PDF bytes
    pdf_bytes = dataland.download_document(reference_id).content

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_bytes)
        tmp_file_path = tmp_file.name

    # Serve the PDF via Streamlit's download_button (creates an HTTP endpoint)
    with Path.open(tmp_file_path, "rb") as f:
        st.download_button("View PDF in browser", f, file_name="document.pdf", mime="application/pdf")
