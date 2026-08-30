
https://github.com/user-attachments/assets/840777e9-9a65-4164-9256-77d304495c72

# Institutional AI Market Terminal & Data Pipeline

An automated, privacy-first financial data pipeline and intelligence terminal. This system ingests daily multi-asset equity data, processes it locally, and leverages a local Large Language Model (Llama 3 via Ollama) to generate quantitative morning briefings.

## System Architecture

*   **Data Ingestion (ETL Layer):** `src/fetch_market_data.py` extracts 30-day historical OHLCV data via Yahoo Finance, handles multi-index schema anomalies, and loads clean datasets into a local `data/raw/` store.
*   **Local Inference Engine:** Utilizes Ollama to run Llama 3 locally, ensuring proprietary portfolio data remains entirely on-device with zero API token costs.
*   **Analytics Interface:** A Streamlit-based dashboard featuring interactive Plotly candlestick charts, 20/50-day SMA technical overlays, and live earnings surprise metrics.
*   **Pipeline Orchestration:** A unified `main.py` entry point handles the sequential execution of the data extraction pipeline and the dashboard deployment.

## Key Engineering Highlights

*   **Resilient Data Parsing:** Custom fallback schemas safely handle API rate limits and structural changes in Yahoo Finance's endpoints without crashing the UI.
*   **Complete Privacy:** No cloud LLM APIs are used. All financial context injection and inference happen locally.
*   **Professional Visualization:** Replaced standard line charts with institutional-grade Plotly interactive subplots (Candlestick + Volume).

## Quickstart Guide

### Prerequisites
*   Python 3.10+
*   [Ollama](https://ollama.ai/) installed with the Llama 3 model downloaded (`ollama run llama3`)

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/rajeshp-pampana/distributed-systems-showcase.git](https://github.com/rajeshp-pampana/distributed-systems-showcase.git)
   cd distributed-systems-showcase

2. Create and activate virtual environment:
   ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows

3. Install dependencies:
   ```bash
    pip install -r requirements.txt

### Execution
Run the orchestrator script to automatically fetch the latest market data and launch the UI:
   ```bash
    python main.py

    ### Step 2: Save and Push to GitHub
    Once you have pasted that in and saved the file (`Ctrl + S`), run these commands in your terminal to push it to your repository:

    ```bash
    git add README.md
    git commit -m "docs: add professional architecture and ETL pipeline README"
    git push

