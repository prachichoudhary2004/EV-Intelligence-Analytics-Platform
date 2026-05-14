import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "bronze")
os.makedirs(DATA_DIR, exist_ok=True)

def generate_india_ev_data():
    print("Generating Indian EV Market Dataset (Production Grade)...")
    
    # States and Cities (Focus on top EV adopters in India)
    states = [
        "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", 
        "Gujarat", "Uttar Pradesh", "Telangana", "Rajasthan",
        "Kerala", "Haryana", "Andhra Pradesh", "Madhya Pradesh"
    ]
    
    # Manufacturers as requested by user
    # 2W: Ola Electric, Ather Energy, TVS iQube, Bajaj, Hero Electric
    # 4W: Tata Motors, Mahindra Electric, MG Motor, BYD India
    oems_2w = ["Ola Electric", "Ather Energy", "TVS iQube", "Bajaj Auto", "Hero Electric"]
    oems_4w = ["Tata Motors", "Mahindra Electric", "MG Motor India", "BYD India", "Hyundai India"]
    
    # Date range (3 years - up to recent)
    dates = pd.date_range(start="2021-04-01", end="2024-04-01", freq="MS")
    
    sales_records = []
    
    for date in dates:
        # Seasonality factor (Festive season in India - Oct/Nov)
        seasonality = 1.3 if date.month in [10, 11] else 1.0
        
        for state in states:
            # State-specific adoption factor
            state_factor = 1.5 if state in ["Delhi", "Maharashtra", "Karnataka"] else 1.0
            
            # Generate 2W sales (Massive growth)
            for oem in oems_2w:
                base_sales = np.random.randint(800, 3000)
                months_passed = (date.year - 2021) * 12 + date.month - 4
                # Exponential growth for 2W (Ola/Ather surge)
                growth = np.exp(months_passed * 0.04) 
                
                # OEM specific tweaks
                oem_factor = 1.8 if oem == "Ola Electric" and months_passed > 12 else 1.0
                
                sales = int(base_sales * growth * seasonality * state_factor * oem_factor * np.random.uniform(0.85, 1.15))
                
                sales_records.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "state": state,
                    "manufacturer": oem,
                    "vehicle_category": "Electric Two Wheeler",
                    "vehicle_segment": "2W",
                    "fuel_type": "Electric",
                    "sales_amount": sales,
                    "price_range": "90,000 - 1,60,000",
                    "battery_capacity": round(np.random.uniform(2.9, 4.0), 1),
                    "charging_time": round(np.random.uniform(4.5, 5.5), 1),
                    "market_share": np.random.uniform(0.1, 0.4) if oem == "Ola Electric" else np.random.uniform(0.05, 0.15)
                })
            
            # Generate 4W sales (Steady growth, Tata dominance)
            for oem in oems_4w:
                base_sales = np.random.randint(100, 600)
                months_passed = (date.year - 2021) * 12 + date.month - 4
                growth = 1 + (months_passed * 0.06)
                
                # Tata Motors market dominance (Nexon/Tiago EV)
                oem_factor = 3.5 if oem == "Tata Motors" else 0.8
                
                sales = int(base_sales * growth * seasonality * state_factor * oem_factor * np.random.uniform(0.9, 1.1))
                
                sales_records.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "state": state,
                    "manufacturer": oem,
                    "vehicle_category": "Electric Four Wheeler",
                    "vehicle_segment": "4W",
                    "fuel_type": "Electric",
                    "sales_amount": sales,
                    "price_range": "14,00,000 - 25,00,000" if oem != "BYD India" else "30,00,000 - 45,00,000",
                    "battery_capacity": round(np.random.uniform(25, 45), 1) if oem != "BYD India" else 71.7,
                    "charging_time": round(np.random.uniform(6, 9), 1),
                    "market_share": np.random.uniform(0.7, 0.8) if oem == "Tata Motors" else np.random.uniform(0.01, 0.05)
                })

    sales_df = pd.DataFrame(sales_records)
    sales_df.to_csv(os.path.join(DATA_DIR, "ev_sales_data.csv"), index=False)
    
    # 2. Charging Stations
    charging_records = []
    for state in states:
        total_stations = np.random.randint(200, 2500)
        fast_chargers = int(total_stations * np.random.uniform(0.25, 0.45))
        charging_records.append({
            "state": state,
            "total_stations": total_stations,
            "fast_chargers": fast_chargers,
            "date_installed": "2024-04-01"
        })
    charging_df = pd.DataFrame(charging_records)
    charging_df.to_csv(os.path.join(DATA_DIR, "charging_stations.csv"), index=False)
    
    # 3. Market Metrics
    market_records = []
    for date in dates:
        for state in states:
            # Higher penetration in Delhi/Karnataka
            p_base = 0.08 if state in ["Delhi", "Karnataka"] else 0.03
            penetration = p_base + (np.random.uniform(0, 0.05))
            
            market_records.append({
                "date": date.strftime("%Y-%m-%d"),
                "state": state,
                "ev_penetration_rate": round(penetration, 4),
                "total_population": np.random.randint(20000000, 120000000),
                "gdp_per_capita": np.random.randint(2000, 6000),
                "gasoline_price": round(np.random.uniform(95, 108), 2),
                "incentives_available": 1 if np.random.random() > 0.1 else 0,
                "state_subsidy_index": round(np.random.uniform(0.2, 0.9), 2),
                "charging_infrastructure_score": round(np.random.uniform(0.3, 0.85), 2)
            })
    market_df = pd.DataFrame(market_records)
    market_df.to_csv(os.path.join(DATA_DIR, "market_metrics.csv"), index=False)
    
    print(f"Dataset generated: {len(sales_df)} sales records across {len(states)} Indian states.")

if __name__ == "__main__":
    generate_india_ev_data()

