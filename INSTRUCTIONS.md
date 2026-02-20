# Monitor Precio Europa - Agent Instructions

This agent monitors bulk wine prices in Europe (Spain, France, Italy) using data from DG AGRI.

## 📂 Project Structure
- **`main.py`**: The Cloud Function code (Extraction & Logic).
- **`logic.py`**: Transaction cost calculation rules.
- **`dashboard.html`**: A local dashboard to view opportunities instantly.
- **`deploy_agent.bat`**: Script to deploy the agent to Google Cloud.
- **`setup_bigquery.py`**: Script to initialize the database in Google Cloud.

## 🚀 Setup & Deployment (Google Cloud)

### Prerequisites
1.  Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install).
2.  Open a terminal and log in: `gcloud auth login`
3.  Set your project: `gcloud config set project [YOUR_PROJECT_ID]`

### Step 1: Initialize Database
Run the setup script to create the BigQuery dataset and table:
```bash
py setup_bigquery.py
```

### Step 2: Deploy Agent
Double-click **`deploy_agent.bat`** or run it in the terminal.
- This will deploy the `extract_dg_agri` function.
- It will also create a **daily cron job (08:00 AM)** to run the agent automatically.

## 📊 Visualization

### Option A: Looker Studio (Cloud)
1.  Go to [Looker Studio](https://lookerstudio.google.com/).
2.  Create a **Blank Report**.
3.  Select **BigQuery** as the data source.
4.  Navigate to `[YOUR_PROJECT] > wine_market_data > prices_staging`.
5.  Visualize the data (Time Series of `precio_eur_hl`, Table with `costo_transaccion_estimado`).

### Option B: Local Dashboard (In this folder)
To see a report *right now* without waiting for the cloud agent:
1.  Run **`py update_dashboard.py`**.
2.  Open **`dashboard.html`** in your browser.
    - It shows the latest price differences and opportunities (Spain -> France/Italy).
