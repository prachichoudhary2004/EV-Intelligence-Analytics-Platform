# ⚡ Enterprise EV Market Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103.1-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.1-red.svg)](https://streamlit.io/)
[![Spark](https://img.shields.io/badge/Apache%20Spark-3.4.1-orange.svg)](https://spark.apache.org/)

An elite-level, recruiter-grade market intelligence platform for the Electric Vehicle (EV) industry. Inspired by the **Databricks Lakehouse Architecture**, this project implements a professional **Medallion Data Pipeline** to transform raw market data into high-fidelity business insights.

---

## 🏗️ Medallion Architecture Overview
Following the industry-standard pattern used in high-scale Databricks environments, the pipeline is organized into three distinct layers:

### 🥉 Bronze Layer (Raw)
*   Stores raw data in its original format (CSV) from various sources: EV Sales, Charging Infrastructure, and Macro-Market Metrics.
*   **Tables**: `bronze.ev_sales`, `bronze.charging_stations`, `bronze.market_metrics`.

### 🥈 Silver Layer (Structured)
*   Cleaned, typed, and deduplicated records.
*   Performs schema normalization and timestamp enrichment.
*   **Tables**: `silver.ev_sales`, `silver.charging_stations`, `silver.market_metrics`.

### 🥇 Gold Layer (Analytical)
*   Business-level datasets optimized for executive reporting and ML forecasting.
*   **Gold.State_Performance**: The "Points Table" of the EV industry, ranking states by adoption and revenue.
*   **Gold.Manufacturer_Insights**: Detailed "Batter Statistics" style metrics for top EV manufacturers (Market Share, Avg Price).
*   **Gold.Infrastructure_Readiness**: "Bowler Statistics" style metrics for charging network density and fast-charger ratios.
*   **Gold.Master_Analytics**: Fully joined feature store for ML modeling.

---

## 🚀 Key Platform Features
*   **Interactive Executive Dashboard**: A premium glassmorphism UI with real-time tickers and state leaderboards.
*   **Semantic KPI Engine**: Centralized logic for CAGR, YoY Growth, and Penetration Indexes.
*   **Executive Narrative Engine**: Automated natural language summaries and strategic recommendations.
*   **Advanced ML Forecaster**: Hybrid pipeline using **XGBoost** and **Prophet** for sales predictions.
*   **Data Health Monitoring**: Integrated DQ checks, schema validation, and health scoring.

---

## 🛠️ Technology Stack
*   **Data Engineering**: Apache Spark (Pandas-simulated), Delta Lake (Parquet-simulated).
*   **Backend**: FastAPI, Uvicorn.
*   **Machine Learning**: XGBoost, Facebook Prophet, Scikit-learn.
*   **Frontend**: Streamlit, Plotly, Custom Glassmorphism CSS.

---

## 📥 Getting Started

### Installation
```bash
pip install -r requirements.txt
```

### Run the Platform
1.  **Initialize & Run ETL**: `python services/spark_engine.py`
2.  **Launch Dashboard**: `streamlit run streamlit_app/app.py`
3.  **Launch API**: `uvicorn api.app:app --reload`

---

## 📊 Project References
This project demonstrates elite engineering practices including Lakehouse data modeling, batch ETL pipelines, and analytical storytelling. Designed for Senior Analytics Engineer / BI Architect roles.
