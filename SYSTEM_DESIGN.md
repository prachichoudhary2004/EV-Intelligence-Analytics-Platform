# System Design Specifications - EV Intelligence Platform

## 1. Data Governance & Medallion Architecture

The platform implements a structured data governance model to ensure data reliability and traceability.

### Bronze Layer (Raw)
- **Source**: Ingested CSV files from market research providers.
- **Format**: Raw CSV.
- **Storage**: `data/bronze/`.
- **Logic**: No transformations; immutable record of truth.

### Silver Layer (Cleaned)
- **Transformation**: Schema enforcement, type conversion, deduplication.
- **Format**: Parquet (optimized for read-heavy operations).
- **Storage**: `data/silver/`.
- **Logic**: `SparkEngine.ingest_bronze_to_silver()`.

### Gold Layer (Curated)
- **Transformation**: Business logic joins, feature engineering, aggregations.
- **Format**: Parquet / Feature Store.
- **Storage**: `data/gold/` and `feature_store/`.
- **Logic**: `SparkEngine.enrich_silver_to_gold()`.

## 2. Analytics Architecture (Semantic Layer)

To prevent business logic fragmentation, all KPI definitions are centralized in the `KPIEngine`.

- **KPI Calculation**: All modules (API, Dashboard, PDF Reports) call the same static methods.
- **Metric Definitions**: 
  - **Penetration Rate**: (EV Sales / Total Population) * 1000.
  - **CAGR**: Standard geometric progression formula.
  - **YoY Growth**: Comparative delta between current and previous year same-month records.

## 3. ML Infrastructure

The forecasting system uses a hybrid approach to balance historical precision with future volatility.

- **Feature Store**: Gold-layer data is flattened into `feature_store/sales_features.parquet` to ensure model training use the exact same features used in the dashboard.
- **XGBoost**: Handles high-dimensional regression and feature importance analysis.
- **Prophet**: Handles seasonality, trend decomposition, and holiday effects in time-series forecasting.

## 4. API & Integration Design

- **FastAPI**: Chosen for its high performance and automatic OpenAPI (Swagger) documentation.
- **Serialization**: All data is exchanged in standard JSON format.
- **Separation of Concerns**: The API layer depends on the `services` layer, ensuring the web interface and API share the same business logic.
