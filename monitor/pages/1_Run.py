import streamlit as st  # noqa: N999
from utils import db, qalab

DEFAULT_QALAB_URL = "http://127.0.0.1:8000"
MODEL_OPTIONS = ["gpt-5", "gpt-4", "gpt-3.5-turbo"]


def _parse_ids(raw_ids: str) -> list[str]:
    return [entry for entry in (item.strip() for item in raw_ids.split(",")) if entry]


def _render_form() -> None:
    experiment_type = (
        st.segmented_control(
            "Select Experiment Type",
            options=["data_point", "dataset"],
            default="data_point",
            key="dp_experiment_type",
        )
        or "data_point"
    )

    qalab_base_url = st.text_input("Enter QaLab Base URL", DEFAULT_QALAB_URL, key="dp_qalab_base_url")
    ids_raw = st.text_area("Enter IDs (Comma separated)", "")
    ids = _parse_ids(ids_raw)
    ai_model = st.selectbox("Select AI Model", MODEL_OPTIONS, key="dp_model")
    use_ocr = st.toggle("Use OCR", value=True, key="dp_ocr")
    override = st.toggle("Override", value=False, key="dp_override")

    if st.button("Start Monitoring Datapoint", type="primary", key="dp_button"):
        if not ids:
            st.error("Please enter at least one ID before starting the experiment.")
            return
        if qalab.is_healthy(qalab_base_url):
            st.success(
                "Started monitoring with model "
                f"{ai_model} and use_ocr={use_ocr}. This might take some time. "
                "You can check the process in the Analytics tab..."
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


def render_run_page() -> None:
    """Render the experiment run page."""
    st.title("Run experiment")
    experiment = db.get_latest_experiment()

    if experiment:
        st.info("An experiment has already been run. Please check the Analytics tab for results.")
        return

    _render_form()


render_run_page()
