import os
import sys
import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config
from utils.logger import logger
from services.data_quality import dq_monitor

try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False
    logger.warning("PySpark not found. Falling back to Pandas-based Spark Simulation.")

class SparkEngine:
    """
    Simulates or executes an enterprise Spark ETL pipeline following the Medallion architecture.
    """
    def __init__(self):
        if SPARK_AVAILABLE:
            self.spark = SparkSession.builder \
                .appName("EVIntelligenceETL") \
                .getOrCreate()
        else:
            self.spark = None

    def ingest_bronze_to_silver(self):
        """
        Process Raw (Bronze) data into Cleaned (Silver) data.
        - Handles types
        - Deduplication
        - Basic filtering
        """
        logger.info("Starting Bronze to Silver transformation...")
        
        # Load Raw Data
        sales_raw = pd.read_csv(config.RAW_SALES_FILE)
        charging_raw = pd.read_csv(config.RAW_CHARGING_FILE)
        market_raw = pd.read_csv(config.RAW_MARKET_FILE)
        
        # Run DQ checks on Bronze
        dq_monitor.check_dataframe(sales_raw, "Bronze_EV_Sales")
        
        # 1. Clean EV Sales
        sales_silver = sales_raw.copy()
        sales_silver['date'] = pd.to_datetime(sales_silver['date'])
        sales_silver = sales_silver.drop_duplicates()
        sales_silver['sales_amount'] = pd.to_numeric(sales_silver['sales_amount'], errors='coerce').fillna(0)
        
        # 2. Clean Charging Stations
        charging_silver = charging_raw.copy()
        charging_silver['date_installed'] = pd.to_datetime(charging_silver['date_installed'])
        charging_silver = charging_silver.drop_duplicates()
        
        # 3. Clean Market Metrics
        market_silver = market_raw.copy()
        market_silver['date'] = pd.to_datetime(market_silver['date'])
        
        # Save to Silver (Simulating Delta Lake with Parquet)
        sales_silver.to_parquet(config.SILVER_DIR / "ev_sales_silver.parquet", index=False)
        charging_silver.to_parquet(config.SILVER_DIR / "charging_stations_silver.parquet", index=False)
        market_silver.to_parquet(config.SILVER_DIR / "market_metrics_silver.parquet", index=False)
        
        logger.info("Silver layer populated successfully.")
        return True

    def enrich_silver_to_gold(self):
        """
        Enrich Silver data into Analytics-ready (Gold) data.
        - Joins
        - Feature engineering
        - Aggregations
        """
        logger.info("Starting Silver to Gold transformation...")
        
        # Load Silver Data
        sales = pd.read_parquet(config.SILVER_DIR / "ev_sales_silver.parquet")
        charging = pd.read_parquet(config.SILVER_DIR / "charging_stations_silver.parquet")
        market = pd.read_parquet(config.SILVER_DIR / "market_metrics_silver.parquet")
        
        # Feature Engineering: Sales Growth & Moving Averages
        sales = sales.sort_values(['state', 'date'])
        sales['sales_rolling_3m'] = sales.groupby('state')['sales_amount'].transform(lambda x: x.rolling(3).mean())
        
        # Join Datasets
        # Aggregating charging by state for joining
        charging_agg = charging.groupby('state').agg({
            'total_stations': 'sum',
            'fast_chargers': 'sum'
        }).reset_index()
        
        gold_df = sales.merge(market, on=['state', 'date'], how='left')
        gold_df = gold_df.merge(charging_agg, on='state', how='left')
        
        # Calculate Advanced Metrics
        gold_df['ev_penetration_index'] = (gold_df['sales_amount'] / gold_df['total_population']) * 1000
        
        # Save to Gold
        gold_df.to_parquet(config.GOLD_DIR / "master_analytics_gold.parquet", index=False)
        
        # Feature Store Generation
        gold_df.to_parquet(config.FEATURE_STORE_DIR / "sales_features.parquet", index=False)
        
        logger.info("Gold layer and Feature Store populated successfully.")
        return gold_df

    def run_pipeline(self):
        """Execute the full Medallion pipeline."""
        self.ingest_bronze_to_silver()
        gold_data = self.enrich_silver_to_gold()
        return gold_data

if __name__ == "__main__":
    engine = SparkEngine()
    engine.run_pipeline()
    print("ETL Pipeline Execution Complete.")
