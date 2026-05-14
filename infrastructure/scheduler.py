import schedule
import time
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("airflow_scheduler")

def trigger_databricks_job():
    """
    Simulates triggering a Databricks Job or an Airflow DAG for Medallion ETL.
    """
    logger.info("Triggering Scheduled ETL Pipeline (Databricks Workflows Simulation)...")
    try:
        subprocess.run(["python", "infrastructure/pipeline_runner.py"], check=True)
        logger.info("ETL Pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

# Run pipeline daily at 2:00 AM
schedule.every().day.at("02:00").do(trigger_databricks_job)

if __name__ == "__main__":
    logger.info("Workflow Orchestrator started. Waiting for scheduled jobs...")
    while True:
        schedule.run_pending()
        time.sleep(60)
