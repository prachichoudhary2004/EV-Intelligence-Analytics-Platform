from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit
from delta.tables import DeltaTable
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import config
from utils.logger import logger

class IncrementalPipeline:
    """
    Handles realistic incremental ETL workflows using Delta Lake.
    """
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def run_incremental_ingest(self, source_path: str, delta_table_path: str, primary_key: str):
        """
        Ingests data incrementally using Delta Lake merge/upsert capabilities.
        """
        logger.info(f"Starting incremental ingest from {source_path} to {delta_table_path}")
        
        # Load new data
        # Assuming new data lands as parquet or csv in bronze
        if source_path.endswith('.csv'):
            new_data_df = self.spark.read.option("header", "true").csv(source_path)
        else:
            new_data_df = self.spark.read.parquet(source_path)
            
        # Add ingestion timestamp
        new_data_df = new_data_df.withColumn("_ingest_timestamp", current_timestamp())

        if not DeltaTable.isDeltaTable(self.spark, delta_table_path):
            logger.info("Delta table does not exist. Performing initial load...")
            # Initial load: save as Delta
            new_data_df.write \
                .format("delta") \
                .mode("overwrite") \
                .option("mergeSchema", "true") \
                .save(delta_table_path)
            logger.info("Initial Delta load complete.")
        else:
            logger.info("Delta table exists. Performing MERGE/UPSERT...")
            delta_table = DeltaTable.forPath(self.spark, delta_table_path)
            
            # Merge condition
            merge_condition = f"target.{primary_key} = source.{primary_key}"
            
            # Execute UPSERT
            delta_table.alias("target") \
                .merge(
                    new_data_df.alias("source"),
                    merge_condition
                ) \
                .whenMatchedUpdateAll() \
                .whenNotMatchedInsertAll() \
                .execute()
                
            logger.info("MERGE/UPSERT complete.")
            
        # Optimize Delta table for read performance
        try:
            delta_table = DeltaTable.forPath(self.spark, delta_table_path)
            delta_table.optimize().executeCompaction()
            logger.info(f"Optimized Delta table at {delta_table_path}")
        except Exception as e:
            logger.warning(f"Failed to optimize Delta table: {e}")

if __name__ == "__main__":
    from pyspark.sql import SparkSession
    spark = SparkSession.builder \
        .appName("IncrementalPipeline") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()
        
    pipeline = IncrementalPipeline(spark)
    # Example usage:
    # pipeline.run_incremental_ingest(str(config.RAW_SALES_FILE), str(config.SILVER_DIR / "sales_delta"), "sale_id")
