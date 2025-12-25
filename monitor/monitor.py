import subprocess
import sys

# Run Streamlit in the background
streamlit_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "monitor/Home.py"])

# Run another script concurrently
other_process = subprocess.Popen([sys.executable, "monitor/scheduled_monitoring.py"])

# Optionally, wait for both to finish
streamlit_process.wait()
other_process.wait()
