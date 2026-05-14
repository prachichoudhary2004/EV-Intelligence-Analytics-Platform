# System Architecture Deep-Dive

## Data Engineering Philosophy
This platform is built on the principle of **Lakehouse Architecture**. It combines the flexibility of a Data Lake (storing raw Parquet/JSON) with the governance and performance of a Data Warehouse.

### 1. Medallion Workflow
We implement a strictly decoupled data flow:

#### **Bronze (Ingestion)**
- **Source**: Simulated real-time API feeds and historical CSVs.
- **State**: Append-only, raw data with original schema.
- **Tools**: PySpark/Pandas script runners.

#### **Silver (Enrichment)**
- **Logic**: Deduplication, type casting (dates, floats), and unit normalization (USD to INR Cr).
- **Quality**: Data Quality Gates verify that critical fields (Sales, Date) are non-null and within expected ranges.
- **Delta Simulation**: Versioning logic ensures we can roll back or audit changes.

#### **Gold (Curation)**
- **Logic**: Star-schema optimization. Joins sales data with infrastructure and manufacturer dimensions.
- **Access**: Optimized for the Streamlit KPI engine and FastAPI endpoints.

---

## Analytics Engineering with dbt
While this project runs in a local environment, the `dbt` folder contains the blueprint for warehouse-scale transformations:
- **Models**: Staging and Mart layers.
- **Testing**: Schema assertions and uniqueness constraints.
- **Documentation**: Column-level descriptions stored in YAML.

---

## Machine Learning Ops
The **Forecasting Engine** is not just a standalone script; it's integrated into the pipeline:
- **Model**: Facebook Prophet chosen for its robustness to seasonal trends in Indian markets.
- **Features**: Time-series extraction from the Gold layer.
- **Monitoring**: MAPE (Mean Absolute Percentage Error) is tracked to signal when model retraining is required.

---

## API Layer
The **FastAPI** gateway provides a RESTful interface for external consumers:
- **Scalability**: Asynchronous design allows for concurrent analytic requests.
- **Documentation**: Automatic Swagger/OpenAPI documentation available at `/docs`.
