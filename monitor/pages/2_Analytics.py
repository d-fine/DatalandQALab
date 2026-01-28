import json  # noqa: N999
from io import BytesIO

import pandas as pd
import streamlit as st
from openpyxl.styles import Font, PatternFill
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
            if row.get("qa_status") == "REJECTED":
                rejected += 1
            elif row.get("qa_status") == "ACCEPTED":
                accepted += 1
            elif row.get("qa_status") == "INCONCLUSIVE":
                inconclusive += 1
            elif row.get("qa_status") == "NOTATTEMPTED":
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


def _create_excel_export(df: pd.DataFrame) -> BytesIO | None:
    """Create formatted Excel file from DataFrame.

    Args:
        df: DataFrame to export with experiment results

    Returns:
        BytesIO buffer containing Excel data with formatted headers and optimized column widths,
        or None if export fails
    """
    try:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Results")
            ws = writer.sheets["Results"]

            # Format header row with bold white text on blue background (only if DataFrame has columns)
            if not df.empty and len(df.columns) > 0:
                for cell in ws[1]:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(fgColor="4472C4", fill_type="solid")

            # Optimize column widths based on content and header length
            for col in ws.columns:
                if col:
                    # Calculate max length from header
                    header_len = len(str(col[0].value or ""))
                    # Calculate max length from data cells
                    data_max = max((len(str(cell.value or "")) for cell in col[1:]), default=0)
                    max_len = max(header_len, data_max)

                    # Set column width with min 10 and max 50 characters
                    ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 10), 50)
    except (ValueError, AttributeError, TypeError) as e:
        st.error(f"❌ Excel export failed: {e}")
        return None
    else:
        buffer.seek(0)
        return buffer


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

    # Create three columns for action buttons
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])

    # Refresh button: reloads the entire page to fetch latest results
    if btn_col1.button("Refresh Results", type="primary", width="stretch"):
        st.rerun()

    # CSV download button
    btn_col2.download_button(
        "📥 Download CSV",
        df.to_csv(index=False),
        "experiment_results.csv",
        "text/csv",
        width="stretch",
    )

    # Excel download button with formatted output
    excel_buffer = _create_excel_export(df)
    if excel_buffer:
        btn_col3.download_button(
            "📥 Download XLSX",
            data=excel_buffer.getvalue(),
            file_name="experiment_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    metrics = _calculate_metrics(qalab_results)

    col1, col2, col3, col4, col5 = st.columns(5)
    col2.metric("Accepted", metrics.get("accepted"))
    col1.metric("Rejected", metrics.get("rejected"))
    col3.metric("Not Attempted", metrics.get("not_attempted"))
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
