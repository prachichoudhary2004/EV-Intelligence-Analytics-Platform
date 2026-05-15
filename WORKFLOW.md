# India EV Market Intelligence Platform - Complete Workflow

This document explains the end-to-end workflow, features, and use cases of the **India EV Market Intelligence Platform**. It provides a step-by-step guide on how data flows from generation to predictive insights.

---

## 1. Data Generation & Ingestion (The Bronze Layer)

The platform begins by simulating a highly realistic, production-grade dataset tailored to the Indian Electric Vehicle market. 

*   **Workflow Step**: The `scripts/generate_india_ev_data.py` script runs to generate raw data.
*   **What it does**: 
    *   Generates 3+ years of historical EV sales data for major Indian states.
    *   Simulates sales numbers for top 2W (Ola, Ather, TVS) and 4W (Tata, Mahindra, MG) manufacturers, incorporating seasonal spikes (e.g., Diwali).
    *   Creates infrastructure data (charging stations, fast chargers).
    *   Generates macro-economic metrics (GDP per capita, gasoline prices, state subsidies).
*   **Output**: Raw CSV files stored in `data/bronze/`.

---

## 2. ETL Processing: The Medallion Lakehouse

Once the raw data is generated, the Spark-based ETL engine cleans and enriches it.

*   **Workflow Step**: The `services/spark_engine.py` executes the transformation pipeline.
*   **Silver Layer (Standardization)**: 
    *   Raw CSV files are loaded into DataFrames.
    *   Data quality checks are performed using the `services/data_quality.py` monitor.
    *   Data types are enforced, null values are handled, and schemas are standardized.
    *   Output: Cleaned Parquet files in `data/silver/`.
*   **Gold Layer (Analytics-Ready)**:
    *   Silver data is aggregated and joined to create business-level tables.
    *   Creates specialized datasets: `state_performance_gold`, `manufacturer_gold`, `infrastructure_gold`, and `master_analytics_gold`.
    *   Output: Highly optimized Parquet tables in `data/gold/` and `data/gold_india/`.

---

## 3. Machine Learning & Forecasting

The platform uses historical data from the Gold layer to train models and predict future market behavior.

*   **Workflow Step**: The `models/forecaster.py` module processes the master analytics data.
*   **Features**:
    *   **Time-Series Forecasting**: Utilizes Prophet to predict the next 12 months of EV adoption.
    *   **Trend Analysis**: Identifies seasonal patterns and long-term growth trajectories.
    *   **Confidence Intervals**: Provides best-case and worst-case scenarios for projected sales.
*   **Use Case**: Allows stakeholders (OEMs, policy makers) to plan inventory, infrastructure rollout, and marketing strategies for the upcoming fiscal year.

---

## 4. Analytics Dashboard (Streamlit)

The processed data and ML predictions are served through a premium, interactive Streamlit dashboard. 

*   **Workflow Step**: Running `streamlit_app/app.py` launches the UI.
*   **Features & Uses**:
    *   **Executive Dashboard**: Provides a high-level national overview. Displays total sales, market revenue, penetration rates, and infrastructure scores. Includes a real-time news/stock ticker.
    *   **Location Analytics**: Deep dive into state-level performance. Interactive maps and scatter plots help identify geographic adoption trends and infrastructure gaps.
    *   **Market Intelligence**: Analyzes ecosystem benchmarking and market segmentation. Highlights which vehicle categories dominate in specific regions.
    *   **Manufacturer Insights**: Tracks OEM market share, pricing strategies vs. sales volume, and competitive positioning.
    *   **Forecasting**: Visualizes the Prophet AI projections.
    *   **Data Health & ML Ops**: A control center for data engineers to monitor pipeline freshness, schema drift, and model accuracy logs.

---

## 5. API Gateway (FastAPI)

For headless integration, the platform provides a robust REST API.

*   **Workflow Step**: Running `api/app.py` via Uvicorn exposes the endpoints.
*   **Features**:
    *   Programmatic access to KPIs, state analytics, and forecasting data.
    *   JSON-formatted responses ready for integration into mobile apps, CRMs, or other enterprise software.
*   **Use Case**: A mobile app developer can query `GET /kpis/market` to display real-time EV adoption metrics in a consumer-facing application.

---

## Summary of the User Journey

1. **The Data Engineer** uses the pipeline scripts to simulate and process millions of rows of data into a clean Medallion architecture.
2. **The Data Scientist** uses the Gold layer data to train and deploy Prophet forecasting models.
3. **The Business Executive** logs into the Streamlit dashboard to view the Executive Dashboard and Manufacturer Insights to make strategic decisions.
4. **The Policy Maker** uses Location Analytics to determine which states require more charging infrastructure subsidies.
5. **The Software Developer** connects to the FastAPI gateway to pull real-time metrics into external applications.
