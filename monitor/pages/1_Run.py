import streamlit as st

from utils import db


st.title("Run experiment")

experiment = db.get_latest_experiment()

if experiment:
    st.info("An experiment has already been run. Please check the Analytics tab for results.")
else:
    dataset_tab, datapoint_tab = st.tabs(["Entire Dataset", "Single Datapoint"])

    with dataset_tab:
        st.header("Monitor an Entire Dataset")
        type = "dataset"
        ids = st.text_area("Enter Dataset IDs (Comma separated)", "").split(",")
        ai_model = st.selectbox("Select AI Model", ["gpt-5", "gpt-4", "gpt-3.5-turbo"])
        use_ocr = st.toggle("Use OCR", value=True)

        if st.button("Start Monitoring Dataset", type="primary"):
            st.success(
                f"Started monitoring with model {ai_model} and use_ocr={use_ocr}. This might take some time. You can check the process in the Analytics tab..."  # noqa: E501
            )
            db.create_experiment(type, ids, ai_model, use_ocr)
    with datapoint_tab:
        st.header("Monitor a Single Datapoint")
        type = "datapoint"
        ids = st.text_area("Enter Datapoint IDs (Comma separated)", "").split(",")
        ai_model = st.selectbox("Select AI Model", ["gpt-5", "gpt-4", "gpt-3.5-turbo"], key="dp_model")
        use_ocr = st.toggle("Use OCR", value=True, key="dp_ocr")

        if st.button("Start Monitoring Datapoint", type="primary", key="dp_button"):
            st.success(
                f"Started monitoring with model {ai_model} and use_ocr={use_ocr}. This might take some time. You can check the process in the Analytics tab..."  # noqa: E501
            )

            db.create_experiment(type, ids, ai_model, use_ocr)
