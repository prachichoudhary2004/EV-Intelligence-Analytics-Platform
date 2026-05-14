# System Architecture - Enterprise EV Platform

## 🏗️ High-Level Overview

The platform is built on a **Medallion Data Architecture** powered by a simulated **Databricks + Spark** ecosystem. It follows a multi-tier structure designed for scalability, observability, and executive-level business intelligence.

## 📊 Data Flow (Medallion Architecture)

```mermaid
graph LR
    subgraph "Data Ingestion"
        A[Bronze: Raw CSVs] --> B[Spark ETL Engine]
    end
    
    subgraph "Data Processing"
        B --> C[Silver: Cleaned Parquet]
        C --> D[Feature Engineering]
        D --> E[Gold: Analytics Master]
    end
    
    subgraph "Intelligence Layers"
        E --> F[Semantic KPI Engine]
        E --> G[ML Feature Store]
        E --> H[Executive Narrative Engine]
    end
    
    subgraph "Consumption"
        F --> I[Streamlit Premium UI]
        G --> J[XGBoost / Prophet Models]
        H --> I
        J --> I
        F --> K[FastAPI Backend]
    end
```

## 🛠️ Technology Stack

- **Data Engineering**: PySpark (ETL), Parquet (Simulated Delta Lake).
- **Analytics Layer**: Pandas, NumPy, Custom KPI Engine.
- **Machine Learning**: XGBoost (Regression), Prophet (Time-Series Forecasting).
- **Backend**: FastAPI (Python).
- **Frontend**: Streamlit (Premium Custom UI).
- **DevOps**: Docker, GitHub Actions (CI/CD).

## 🛡️ Enterprise Engineering Practices

1. **Data Quality Monitoring**: Automated schema validation and health scoring via `services/data_quality.py`.
2. **Semantic Layer**: Centralized business logic in `services/kpi_engine.py` to ensure consistency across UI and API.
3. **MLOps awareness**: Decoupled feature store and modular model training.
4. **Professional UI**: Custom CSS-driven Design System with glassmorphism and modern typography.
