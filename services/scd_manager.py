import os
import sys
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_date, when
from pyspark.sql.window import Window

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logger

class SCDManager:
    """
    Handles Slowly Changing Dimensions (SCD Type 2) logic.
    Tracks historical changes in reference data (e.g., policy, manufacturer metadata).
    """
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def apply_scd2(self, target_df_path: str, source_df, primary_key: str, business_cols: list):
        """
        Updates an SCD Type 2 dimension table.
        """
        logger.info(f"Applying SCD Type 2 on {target_df_path} using key {primary_key}")
        
        from delta.tables import DeltaTable
        
        # Ensure we have standard SCD columns in the source payload
        source_df = source_df \
            .withColumn("valid_from", current_date()) \
            .withColumn("valid_to", lit(None).cast("date")) \
            .withColumn("current_flag", lit(True))
            
        if not DeltaTable.isDeltaTable(self.spark, target_df_path):
            logger.info("Target table does not exist. Initializing SCD2 table...")
            source_df.write.format("delta").mode("overwrite").save(target_df_path)
            return
            
        target_table = DeltaTable.forPath(self.spark, target_df_path)
        
        # 1. Identify records to expire (they exist in target, are current, and data has changed)
        # Create a condition to check if any business column changed
        change_cond = " OR ".join([f"source.{c} != target.{c}" for c in business_cols])
        
        # Perform MERGE to expire old records
        target_table.alias("target").merge(
            source_df.alias("source"),
            f"target.{primary_key} = source.{primary_key} AND target.current_flag = true AND ({change_cond})"
        ).whenMatchedUpdate(
            set={
                "valid_to": current_date(),
                "current_flag": lit(False)
            }
        ).execute()
        
        # 2. Identify entirely new records OR records that just got expired (and need a new active row inserted)
        # For this simulated environment, we append the source DataFrame for new and changed rows.
        # A more robust enterprise implementation uses complex staged merges.
        
        # Find which rows in source_df need to be inserted
        target_df = self.spark.read.format("delta").load(target_df_path)
        
        # We insert if the primary_key is entirely new, OR if the current_flag is now False (meaning we just expired it above).
        existing_keys = target_df.filter("current_flag = true").select(primary_key)
        
        inserts_df = source_df.join(existing_keys, on=primary_key, how="left_anti")
        
        if inserts_df.count() > 0:
            inserts_df.write.format("delta").mode("append").save(target_df_path)
            
        logger.info("SCD Type 2 apply completed.")
