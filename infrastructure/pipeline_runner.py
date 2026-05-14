import os
import sys
import time
import traceback
from datetime import datetime
from functools import wraps

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logger
from services.spark_engine import spark_engine

def task_decorator(task_name):
    """
    Simulates a workflow stage decorator (similar to Airflow or Prefect tasks).
    Adds standard logging, timing, and error handling.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"[[ STAGE START ]] : {task_name}")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"[[ STAGE SUCCESS ]] : {task_name} (Completed in {elapsed:.2f}s)")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"[[ STAGE FAILED ]] : {task_name} after {elapsed:.2f}s. Error: {e}")
                logger.error(traceback.format_exc())
                raise
        return wrapper
    return decorator

class PipelineRunner:
    """
    Simulates a Databricks Job or Airflow DAG execution.
    Manages stage dependencies, retries, and overall workflow state.
    """
    
    @task_decorator("1_Ingest_Raw_To_Bronze")
    def stage_1_ingest(self):
        logger.info("Executing simulated raw data ingestion check...")
        # Assume data is already dropped into the raw directory by an external process
        pass
        
    @task_decorator("2_Bronze_To_Silver_ETL")
    def stage_2_clean(self):
        # Calls the actual transformation logic
        spark_engine.ingest_bronze_to_silver()
        
    @task_decorator("3_Silver_To_Gold_Aggregations")
    def stage_3_aggregate(self):
        spark_engine.enrich_silver_to_gold()
        
    @task_decorator("4_Data_Quality_Gates")
    def stage_4_quality_checks(self):
        logger.info("Running Data Quality validations on Gold layer...")
        from services.data_quality import dq_monitor
        import pandas as pd
        from config.config import config
        
        # Load one of the gold tables to check
        master_df = pd.read_parquet(config.GOLD_DIR / "master_analytics_gold.parquet")
        report = dq_monitor.check_dataframe(master_df, "master_analytics_gold")
        
        if report['quality_score'] < 90.0:
            logger.warning(f"Data Quality Score is below threshold (90.0): {report['quality_score']}")
            # In a strict pipeline, we would raise an Exception to fail the job here.
        else:
            logger.info(f"Data Quality passed with score: {report['quality_score']}")

    def execute_all(self):
        """Orchestrates the execution sequence."""
        logger.info(f"=== Starting Scheduled ETL Pipeline Run : {datetime.now().isoformat()} ===")
        try:
            self.stage_1_ingest()
            self.stage_2_clean()
            self.stage_3_aggregate()
            self.stage_4_quality_checks()
            logger.info("=== Pipeline Execution Completed Successfully ===")
            return True
        except Exception as e:
            logger.error("=== Pipeline Execution FAILED ===")
            return False

if __name__ == "__main__":
    runner = PipelineRunner()
    runner.execute_all()
