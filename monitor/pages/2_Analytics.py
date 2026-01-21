import json  # noqa: N999

import pandas as pd
import streamlit as st
from utils import db


def _calculate_metrics(data: dict) -> dict:
    """Calculate metrics from the results data."""
    total = len(data)

    rejected = 0
    accepted = 0
    inconclusive = 0
    not_attempted = 0

    for row in data:
        if isinstance(row, dict):
            if row.get("qa_status") == "QaRejected":
                rejected += 1
            elif row.get("qa_status") == "QaAccepted":
                accepted += 1
            elif row.get("qa_status") == "QaInconclusive":
                inconclusive += 1
            elif row.get("qa_status") == "QaNotAttempted":
                not_attempted += 1

    return {
        "total": total,
        "rejected": rejected,
        "accepted": accepted,
        "inconclusive": inconclusive,
        "not_attempted": not_attempted,
    }


def _format_db_response(db_response: tuple, experiment_type: str) -> list:
    """Format database response into a CSV BytesIO stream."""
    if experiment_type == "dataset":
        return [v for row in db_response for v in json.loads(row[3]).values()]
    return [json.loads(row[3]) for row in db_response]


st.title("Experiment Analytics")

experiment_id, experiment_type, ids, model, use_ocr, override, qalab_base_url, timestamp = (
    db.get_latest_experiment()
    or (
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
)


if experiment_id:
    st.markdown(f"""
Currently running an experiment with the following attributes:

- Model: {model}
- Use OCR: {bool(use_ocr)}
- Type: {experiment_type}
""")

    with st.expander("Open IDs"):
        st.text_area("IDs being processed: ", ids, disabled=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    data = db.get_results_by_experiment(experiment_id)
    qalab_results = _format_db_response(data, experiment_type=experiment_type)

    df = pd.DataFrame(qalab_results)
    # check if the df has the dataframe column "file_reference"

    if "file_reference" in df:
        df["View PDF"] = df["file_reference"].apply(lambda x: f"/PDF_Viewer?reference_id={x!s}")

    col1, col2 = st.columns([1, 1])
    if col1.button("Refresh Results", type="primary", width="stretch"):
        data = db.get_results_by_experiment(experiment_id)
    col2.download_button(
        "📥 Download CSV", df.to_csv(index=False), "experiment_results.csv", "text/csv", width="stretch"
    )

    metrics = _calculate_metrics(qalab_results)

    col1, col2, col3, col4, col5 = st.columns(5)
    col2.metric("Accepted", metrics.get("accepted"))
    col1.metric("Rejected", metrics.get("rejected"))
    col3.metric("Not Attempted", metrics.get("not_attempted"))
    col4.metric("Inconclusive", metrics.get("inconclusive"))
    col5.metric("Total Processed", metrics.get("total"))

    st.dataframe(
        df,
        width="stretch",
        column_config={"View PDF": st.column_config.LinkColumn("View PDF", display_text="📄 Open")},
    )

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
