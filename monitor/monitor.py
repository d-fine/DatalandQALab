import subprocess

# Run Streamlit in the background
streamlit_process = subprocess.Popen(["streamlit", "run", "monitor/app.py"])

# Run another script concurrently
other_process = subprocess.Popen(["python", "monitor/scheduled_monitoring.py"])

# Optionally, wait for both to finish
streamlit_process.wait()
other_process.wait()
