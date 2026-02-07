import streamlit as st


def render_home() -> None:
    """Render the home page of the monitor application."""
    st.set_page_config(
        page_title="Monitor Server",
        layout="wide",
    )

    st.title("DatalandQaLab Monitor")
    st.markdown(
        """
        This is the monitor application for DatalandQaLab. Use the sidebar to navigate between different sections.
        - [Run a new experiment](Run) to start monitoring new documents.
        - View [Experiment Analytics](Analytics) for insights from the last run.
        """
    )


render_home()
