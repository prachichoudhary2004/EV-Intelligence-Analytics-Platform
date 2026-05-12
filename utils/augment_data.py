import os
import sys
import pandas as pd
import numpy as np

# Add parent so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from config.config import config

def augment_data():
    """
    Creates fake time series data from single date.
    """
    print("Augmenting data for multi-month time series...")
    
    # Load raw data
    sales_df = pd.read_csv(config.RAW_SALES_FILE)
    market_df = pd.read_csv(config.RAW_MARKET_FILE)
    
    # Make 24 months of data
    start_date = datetime(2022, 1, 1)
    dates = [start_date + pd.DateOffset(months=i) for i in range(24)]
    
    new_sales_list = []
    new_market_list = []
    
    for date in dates:
        # Sales Augmentation
        temp_sales = sales_df.copy()
        temp_sales['date'] = date
        # Ensure numeric
        temp_sales['sales_amount'] = pd.to_numeric(temp_sales['sales_amount'], errors='coerce').fillna(0)
        # Add growth and random changes
        growth_factor = 1 + (dates.index(date) * 0.05) + np.random.normal(0, 0.02)
        temp_sales['sales_amount'] = (temp_sales['sales_amount'] * growth_factor).astype(int)
        new_sales_list.append(temp_sales)
        
        # Market Augmentation
        temp_market = market_df.copy()
        temp_market['date'] = date
        # Ensure numeric
        temp_market['ev_penetration_rate'] = pd.to_numeric(temp_market['ev_penetration_rate'], errors='coerce').fillna(0)
        temp_market['ev_penetration_rate'] = temp_market['ev_penetration_rate'] * growth_factor
        new_market_list.append(temp_market)
        
    augmented_sales = pd.concat(new_sales_list)
    augmented_market = pd.concat(new_market_list)
    
    # Save back to bronze files
    augmented_sales.to_csv(config.RAW_SALES_FILE, index=False)
    augmented_market.to_csv(config.RAW_MARKET_FILE, index=False)
    
    print(f"Data augmentation complete. Generated 24 months of data for {len(sales_df)} records.")

if __name__ == "__main__":
    augment_data()
