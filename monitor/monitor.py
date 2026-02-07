import logging
import subprocess
import sys
from collections.abc import Sequence

logger = logging.getLogger("qa_lab_monitor")


def _start_process(command: Sequence[str]) -> subprocess.Popen:
    logger.info("Starting process: %s", " ".join(command))
    return subprocess.Popen(command)


def main() -> None:
    """Start the Streamlit app and scheduled monitoring process."""
    logging.basicConfig(level=logging.INFO)
    streamlit_process = _start_process([sys.executable, "-m", "streamlit", "run", "monitor/Home.py"])
    scheduled_process = _start_process([sys.executable, "monitor/scheduled_monitoring.py"])

    try:
        streamlit_process.wait()
        scheduled_process.wait()
    except KeyboardInterrupt:
        logger.info("Shutting down processes...")
        streamlit_process.terminate()
        scheduled_process.terminate()
    finally:
        streamlit_process.wait()
        scheduled_process.wait()


if __name__ == "__main__":
    main()
