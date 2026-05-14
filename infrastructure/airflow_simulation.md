# 🔄 Workflow Orchestration & Job Automation

This project simulates a production **Data Engineering Orchestration** setup. While the current execution is driven by a custom Python pipeline runner, it is designed to map directly to enterprise tools like **Databricks Workflows** or **Apache Airflow**.

## Databricks Workflows Mapping

If deployed to Databricks, the tasks mapped in `pipeline_runner.py` translate to a standard DAG (Directed Acyclic Graph) in Workflows:

1. **Task 1: `ingest_bronze`** (Ingest API / CSV to Azure Data Lake / S3)
2. **Task 2: `bronze_to_silver`** (Clean, cast types, track SCD Type 2 using Delta Lake `MERGE`)
3. **Task 3: `silver_to_gold`** (dbt Cloud trigger for Gold aggregations & KPI modeling)
4. **Task 4: `ml_forecast_inference`** (Prophet model prediction job)
5. **Task 5: `data_quality_gates`** (Great Expectations validation step)

## Airflow DAG Example

A standard Airflow implementation for this project would look like:

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule_interval="0 2 * * *", start_date=datetime(2024, 1, 1), catchup=False)
def ev_market_intelligence_dag():

    @task
    def run_dbt_models():
        # Triggers the Gold layer dbt models
        pass

    @task
    def run_data_quality():
        # Validates data against predefined constraints
        pass

    run_dbt_models() >> run_data_quality()

ev_dag = ev_market_intelligence_dag()
```

See `infrastructure/scheduler.py` for a lightweight local cron-based simulation using the Python `schedule` library.
