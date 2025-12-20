import streamlit as st


st.title("Run a new experiment")


dataset_tab, datapoint_tab = st.tabs(["Entire Dataset", "Sigle Datapoint"])


with dataset_tab:
    st.header("Monitor an Entire Dataset")
    dataset_ids = st.text_area("Enter Dataset IDs (Comma separated)", "")
    ai_model = st.selectbox("Select AI Model", ["gpt-5", "gpt-4", "gpt-3.5-turbo"])
    use_ocr = st.toggle("Use OCR", value=True)

    if st.button("Start Monitoring Dataset", type="primary"):
        # make it a nice alert box
        st.success(
            f"Started monitoring dataset {dataset_ids} with model {ai_model} and use_ocr={use_ocr}. This might take some time. You can check the process in the Analytics tab..."
        )
