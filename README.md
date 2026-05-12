# ⚡ Enterprise EV Market Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103.1-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.1-red.svg)](https://streamlit.io/)
[![Spark](https://img.shields.io/badge/Apache%20Spark-3.4.1-orange.svg)](https://spark.apache.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An elite-level, recruiter-grade market intelligence platform for the Electric Vehicle (EV) industry. This project transforms raw market data into high-fidelity business insights using a **Medallion Architecture**, **PySpark ETL pipelines**, and **Advanced ML Forecasting**.

---

## 🏗️ Professional Architecture

The platform follows modern enterprise engineering standards:

*   **Medallion Data Architecture**: 
    *   **Bronze**: Raw data ingestion.
    *   **Silver**: Cleaned, typed, and deduplicated records.
    *   **Gold**: Analytics-ready "Master Tables" and Feature Stores.
*   **Semantic KPI Engine**: Centralized business logic for consistent metric calculation (CAGR, YoY, Penetration).
*   **Executive Narrative Engine**: Automated natural language summaries and strategic recommendations.
*   **Hybrid ML Pipeline**: Combining **XGBoost** for short-term regression and **Prophet** for long-term time-series forecasting.
*   **FastAPI Backend**: A production-ready API layer for external data consumption.

---

## 🚀 Key Features

*   **Premium Dark UI**: Glassmorphism design system with custom CSS and animated KPI cards.
*   **Executive Dashboard**: Real-time market overview with high-fidelity visuals.
*   **Advanced Analytics**: State-level benchmarking against national averages.
*   **ML Forecasting**: Integrated time-series predictions with confidence intervals.
*   **Data Health Monitoring**: Health scoring, schema validation, and drift detection.
*   **Enterprise Reporting**: Automated PDF executive summaries and CSV data exports.
*   **Live Market Ticker**: Simulated real-time market data feed.

---

## 🛠️ Technology Stack

| Layer | Technology |
| --- | --- |
| **Data Engineering** | Databricks (Simulated), Apache Spark, Parquet |
| **Backend / API** | Python, FastAPI, Uvicorn |
| **Machine Learning** | XGBoost, Facebook Prophet, Scikit-learn |
| **Analytics** | Pandas, NumPy, KPI Engine |
| **Frontend** | Streamlit, Plotly, Custom CSS |
| **Reporting** | FPDF2, CSV Serialization |

---

## 📥 Getting Started

### Prerequisites
*   Python 3.9+
*   Java (for PySpark, optional simulation mode available)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ev-intelligence-platform.git

# Install dependencies
pip install -r requirements.txt
```

### Run the Platform
1.  **Run ETL Pipeline**: `python services/spark_engine.py`
2.  **Train ML Models**: `python models/forecaster.py`
3.  **Launch Dashboard**: `streamlit run streamlit_app/app.py`
4.  **Launch API**: `uvicorn api.app.py:app --reload`

---

## 📊 Documentation
*   [Architecture Deep Dive](ARCHITECTURE.md)
*   [System Design Specifications](SYSTEM_DESIGN.md)
*   [Product Roadmap](ROADMAP.md)

