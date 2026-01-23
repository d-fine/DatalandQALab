import streamlit as st  # noqa: N999
from utils import db, qalab

st.title("Run experiment")

experiment = db.get_latest_experiment()

if experiment:
    st.info("An experiment has already been run. Please check the Analytics tab for results.")
else:
    experiment_type = st.segmented_control(
        "Select Experiment Type", options=["data_point", "dataset"], default="data_point", key="dp_experiment_type"
    )

    qalab_base_url = st.text_input("Enter QaLab Base URL", "http://127.0.0.1:8000", key="dp_qalab_base_url")
    ids = st.text_area("Enter IDs (Comma separated)", "").replace(" ", "").split(",")
    ai_model = st.selectbox("Select AI Model", ["gpt-5", "gpt-4", "gpt-3.5-turbo"], key="dp_model")
    use_ocr = st.toggle("Use OCR", value=True, key="dp_ocr")
    override = st.toggle("Override", value=False, key="dp_override")

    if st.button("Start Monitoring Datapoint", type="primary", key="dp_button"):
        if qalab.is_healthy(qalab_base_url):
            st.success(
                f"Started monitoring with model {ai_model} and use_ocr={use_ocr}. This might take some time. You can check the process in the Analytics tab..."  # noqa: E501
            )

            db.create_experiment(
                experiment_type=experiment_type,
                ids=ids,
                ai_model=ai_model,
                use_ocr=use_ocr,
                override=override,
                qalab_base_url=qalab_base_url,
            )
            st.rerun()
        else:
            st.error("The provided QaLab Base URL is not reachable. Please check and try again.")
