import streamlit as st

from utils import db, qalab


st.title("Run experiment")

experiment = db.get_latest_experiment()

if experiment:
    st.info("An experiment has already been run. Please check the Analytics tab for results.")
else:
    dataset_tab, datapoint_tab = st.tabs(["Entire Dataset", "Single Datapoint"])

    with dataset_tab:
        st.header("Monitor an Entire Dataset")
        experiment_type = "dataset"
        qalab_base_url = st.text_input("Enter QaLab Base URL", "http://127.0.0.1:8000")
        ids = st.text_area("Enter Dataset IDs (Comma separated)", "").split(",")
        ai_model = st.selectbox("Select AI Model", ["gpt-5", "gpt-4", "gpt-3.5-turbo"])
        use_ocr = st.toggle("Use OCR", value=True)
        override = st.toggle("Override Existing Experiment", value=False)

        if st.button("Start Monitoring Dataset", type="primary"):
            if qalab.is_healthy(qalab_base_url):
                st.success(
                    f"Started monitoring with model {ai_model}, override={override} and use_ocr={use_ocr}. This might take some time. You can check the process in the Analytics tab..."  # noqa: E501
                )
                db.create_experiment(
                    experiment_type=experiment_type,
                    ids=ids,
                    ai_model=ai_model,
                    use_ocr=use_ocr,
                    override=override,
                    qalab_base_url=qalab_base_url,
                )
            else:
                st.error("The provided QaLab Base URL is not reachable. Please check and try again.")

    with datapoint_tab:
        st.header("Monitor a Single Datapoint")
        experiment_type = "data_point"
        qalab_base_url = st.text_input("Enter QaLab Base URL", "http://127.0.0.1:8000", key="dp_qalab_base_url")
        ids = st.text_area("Enter Datapoint IDs (Comma separated)", "").split(",")
        ai_model = st.selectbox("Select AI Model", ["gpt-5", "gpt-4", "gpt-3.5-turbo"], key="dp_model")
        use_ocr = st.toggle("Use OCR", value=True, key="dp_ocr")
        override = st.toggle("Override Existing Experiment", value=False, key="dp_override")

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
            else:
                st.error("The provided QaLab Base URL is not reachable. Please check and try again.")
