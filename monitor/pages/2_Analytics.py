import time
import json
import streamlit as st
from utils import db

st.title("Experiment Analytics")

id, type, ids, model, use_ocr, timestamp = db.get_latest_experiment() or (None, None, None, None, None, None)


if id:
    with st.expander("Experiment Details"):
        st.markdown(f"""
Currently running an experiment with the following attributes:

- Model: {model}
- Use OCR: {bool(use_ocr)}
- Type: {type}
- IDs:
{"".join([f"  - {id_}\n" for id_ in json.loads(ids)]) if ids else "  - None"}
""")

    results = db.get_results_by_experiment(id)
    if st.button("Refresh Results", type="primary"):
        results = db.get_results_by_experiment(id)

    st.dataframe(results)

    with st.popover("Reset experiment"):
        st.warning("This action cannot be undone.")
        confirm = st.checkbox("Yes, I understand the consequences")

        if st.button("Confirm delete", disabled=not confirm):
            st.success("All entries deleted.")
            db.reset_experiment()
            st.rerun()
else:
    st.info("No experiments found. Please run a new experiment in the 'Run' tab.")
