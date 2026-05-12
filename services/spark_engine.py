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
    Runs our ETL pipeline using Spark or Pandas.
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
        Clean up raw data and make it usable.
        - Fix data types
        - Remove duplicates
        - Basic cleanup
        """
        logger.info("Starting Bronze to Silver transformation...")
        
        # Load the raw files
        sales_raw = pd.read_csv(config.RAW_SALES_FILE)
        charging_raw = pd.read_csv(config.RAW_CHARGING_FILE)
        market_raw = pd.read_csv(config.RAW_MARKET_FILE)
        
        # Check data quality on raw data
        dq_monitor.check_dataframe(sales_raw, "Bronze_EV_Sales")
        
        # 1. Clean up sales data
        sales_silver = sales_raw.copy()
        sales_silver['date'] = pd.to_datetime(sales_silver['date'])
        sales_silver = sales_silver.drop_duplicates()
        sales_silver['sales_amount'] = pd.to_numeric(sales_silver['sales_amount'], errors='coerce').fillna(0)
        
        # 2. Clean up charging station data
        charging_silver = charging_raw.copy()
        charging_silver['date_installed'] = pd.to_datetime(charging_silver['date_installed'])
        charging_silver = charging_silver.drop_duplicates()
        
        # 3. Clean up market metrics
        market_silver = market_raw.copy()
        market_silver['date'] = pd.to_datetime(market_silver['date'])
        
        # Save to silver layer (using Parquet like Delta Lake)
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
        
        # 0. Create Enriched Base (for all Gold tables)
        # We need to simulate 'price' for revenue calculation if not present
        if 'price' not in sales.columns:
            # Assigning a synthetic price based on price_range or random
            sales['price'] = np.random.randint(35000, 75000, size=len(sales))
        
        sales['revenue'] = sales['sales_amount'] * sales['price']
        
        charging_agg = charging.groupby('state').agg({
            'total_stations': 'sum',
            'fast_chargers': 'sum'
        }).reset_index()
        
        base_df = sales.merge(market, on=['state', 'date'], how='left')
        base_df = base_df.merge(charging_agg, on='state', how='left')
        
        # 1. Gold: State Performance (Leaderboard style)
        logger.info("Generating Gold: State Performance...")
        state_performance = base_df.groupby('state').agg({
            'sales_amount': 'sum',
            'revenue': 'sum',
            'ev_penetration_rate': 'mean'
        }).reset_index()
        state_performance['rank'] = state_performance['sales_amount'].rank(ascending=False)
        state_performance.to_parquet(config.GOLD_DIR / "state_performance_gold.parquet", index=False)
        
        # 2. Gold: Manufacturer Market Share
        logger.info("Generating Gold: Manufacturer Insights...")
        manufacturer_gold = base_df.groupby('manufacturer').agg({
            'sales_amount': 'sum',
            'revenue': 'sum',
            'market_share': 'mean'
        }).reset_index()
        manufacturer_gold.to_parquet(config.GOLD_DIR / "manufacturer_gold.parquet", index=False)
        
        # 3. Gold: Infrastructure Readiness
        logger.info("Generating Gold: Infrastructure Readiness...")
        infra_gold = base_df.groupby('state').agg({
            'total_stations': 'first',
            'fast_chargers': 'first',
            'ev_penetration_rate': 'mean'
        }).reset_index()
        infra_gold['fast_charger_ratio'] = infra_gold['fast_chargers'] / infra_gold['total_stations']
        infra_gold.to_parquet(config.GOLD_DIR / "infrastructure_gold.parquet", index=False)
        
        # 4. Master Analytics Table (Full grain)
        base_df['ev_penetration_index'] = (base_df['sales_amount'] / base_df['total_population']) * 1000
        base_df.to_parquet(config.GOLD_DIR / "master_analytics_gold.parquet", index=False)
        
        # Feature Store Generation
        base_df.to_parquet(config.FEATURE_STORE_DIR / "sales_features.parquet", index=False)
        
        logger.info("All Gold tables and Feature Store populated successfully.")
        return base_df

    def run_pipeline(self):
        """Run the whole ETL pipeline."""
        self.ingest_bronze_to_silver()
        gold_data = self.enrich_silver_to_gold()
        return gold_data

# Easy to import anywhere
spark_engine = SparkEngine()

if __name__ == "__main__":
    spark_engine.run_pipeline()
    print("ETL Pipeline Execution Complete.")
