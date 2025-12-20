import json
from io import BytesIO

import pandas as pd
import streamlit as st
from utils import db


def _calculate_metrics(data) -> dict:
    """Calculate metrics from the results data."""
    total = len(data)
    rejected = sum(1 for row in data if row["qa_status"] == "Rejected")
    accepted = sum(1 for row in data if row["qa_status"] == "Accepted")
    incomplete = sum(1 for row in data if row["qa_status"] == "Incomplete")
    inconclusive = sum(1 for row in data if row["qa_status"] == "Inconclusive")

    return {
        "total": total,
        "rejected": rejected,
        "accepted": accepted,
        "incomplete": incomplete,
        "inconclusive": inconclusive,
    }


st.title("Experiment Analytics")

id, type, ids, model, use_ocr, timestamp = db.get_latest_experiment() or (None, None, None, None, None, None)


if id:
    st.markdown(f"""
Currently running an experiment with the following attributes:

- Model: {model}
- Use OCR: {bool(use_ocr)}
- Type: {type}
""")

    st.markdown("<hr>", unsafe_allow_html=True)

    data = db.get_results_by_experiment(id)
    qalab_results = [json.loads(row[3]) for row in data]
    df = pd.DataFrame(qalab_results)

    col1, col2 = st.columns([1, 1])
    if col1.button("Refresh Results", type="primary", width="stretch"):
        data = db.get_results_by_experiment(id)
    col2.download_button(
        "📥 Download CSV", df.to_csv(index=False), "experiment_results.csv", "text/csv", width="stretch"
    )

    metrics = _calculate_metrics(qalab_results)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Rejected", metrics.get("rejected"))
    col2.metric("Accepted", metrics.get("accepted"))
    col3.metric("Incomplete", metrics.get("incomplete"))
    col4.metric("Inconclusive", metrics.get("inconclusive"))
    col5.metric("Total Processed", metrics.get("total"))

    st.dataframe(qalab_results, width="stretch")

    st.markdown("<hr>", unsafe_allow_html=True)
    with st.popover("Reset experiment"):
        st.warning("This action cannot be undone.")
        confirm = st.checkbox("Yes, I understand the consequences")

        if st.button("Confirm delete", disabled=not confirm):
            st.success("All entries deleted.")
            db.reset_experiment()
            st.rerun()
else:
    st.info("No experiments found. Please run a new experiment in the 'Run' tab.")
