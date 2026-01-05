# DatalandQALab Monitor Dashboard - User Guide

This guide describes how to configure experiments, monitor data points and datasets using AI models, and analyze results using the Monitor Dashboard.

## 1. Establish Connection (SSH Tunnel)
Since the dashboard runs on a protected server, you must access it via an SSH tunnel.

1. Open a terminal on your local machine.
2. Run the following command to forward the port:
   ```bash
   ssh -L 8501:127.0.0.1:8501 ubuntu@qalab-dev.duckdns.org
   ```
3. **Keep this terminal open** as long as you want to use the dashboard.

## 2. Start the System
You need to start the Backend and Frontend services on the server (inside the SSH session).

Run the following commands sequentially:

1. **Start Backend:**
   ```bash
   pdm run dev
   ```
2. **Start Dashboard:**
   ```bash
   pdm run monitor
   ```
3. **Access:** Open your local browser at `http://127.0.0.1:8051`.

## 3. Run an Experiment
Navigate to the **Run** section in the sidebar to configure a test.

1. **Experiment Type:** Choose `data_point`or `dataset`.
2. **QaLab Base URL:** Enter `http://qalab-qa-lab-server-prod-1:81`.
3. **IDs:** Enter the IDs (comma separated).
4. **AI Model:** Select the model (e.g. `gpt-5`).
5. **Use OCR:** Toggle on for text recognition.
6. **Start:** Click **Start Monitoring Datapoint**.

## 4. Analytics and Exporting Data
View real-time progress in the **Analytics** section. To analyze the data in Excel, follow this specific workflow:

1. **Export:** Click **Download CSV** in the dashboard.
2. **Convert:** Use a **CSV to Excel Converter** tool to convert the file.
3. **Format in Excel:**
   * Open the converted Excel file.
   * Select the first column
   * Go to **Data > Text to Columns**.
   * **Delimited**, set the separator to **Comma**, and finish.
4. **Create Intelligent Table:**
   * Select all data.
   * Press `Ctrl + T (or Cmd + T)`
   * **My table has headers** and confirm.
  
You can now use the filter headers to analyze the results. 
   
