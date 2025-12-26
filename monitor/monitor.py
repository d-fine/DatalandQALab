import logging
import subprocess
import sys

logger = logging.getLogger("qa_lab_monitor")

streamlit_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "monitor/Home.py"])

other_process = subprocess.Popen([sys.executable, "monitor/scheduled_monitoring.py"])

streamlit_process.wait()
other_process.wait()
