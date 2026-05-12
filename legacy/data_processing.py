import pandas as pd
import numpy as np
from datetime import datetime
import os

class EVDataProcessor:
    def __init__(self, raw_data_path='data/raw/', processed_data_path='data/processed/'):
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        self.ensure_directories()
    
    def ensure_directories(self):
        os.makedirs(self.processed_data_path, exist_ok=True)
    
    def load_data(self):
        self.ev_sales = pd.read_csv(os.path.join(self.raw_data_path, 'ev_sales_data.csv'))
        self.charging_stations = pd.read_csv(os.path.join(self.raw_data_path, 'charging_stations.csv'))
        self.market_metrics = pd.read_csv(os.path.join(self.raw_data_path, 'market_metrics.csv'))
    
    def clean_ev_sales(self):
        df = self.ev_sales.copy()
        
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        
        df['sales_amount'] = pd.to_numeric(df['sales_amount'], errors='coerce')
        df['battery_capacity'] = pd.to_numeric(df['battery_capacity'], errors='coerce')
        df['charging_time'] = pd.to_numeric(df['charging_time'], errors='coerce')
        df['market_share'] = pd.to_numeric(df['market_share'], errors='coerce')
        
        df['price_min'] = df['price_range'].str.extract(r'(\d+)').astype(float) * 1000
        df['price_max'] = df['price_range'].str.extract(r'-(\d+)').astype(float) * 1000
        df['price_avg'] = (df['price_min'] + df['price_max']) / 2
        
        df['revenue'] = df['sales_amount'] * df['price_avg']
        
        df = df.dropna(subset=['sales_amount', 'manufacturer', 'state'])
        
        self.ev_sales_clean = df
        return df
    
    def clean_charging_stations(self):
        df = self.charging_stations.copy()
        
        df['date_installed'] = pd.to_datetime(df['date_installed'])
        df['installation_age_days'] = (datetime.now() - df['date_installed']).dt.days
        
        df['total_stations'] = pd.to_numeric(df['total_stations'], errors='coerce')
        df['fast_chargers'] = pd.to_numeric(df['fast_chargers'], errors='coerce')
        df['slow_chargers'] = pd.to_numeric(df['slow_chargers'], errors='coerce')
        df['avg_power_kw'] = pd.to_numeric(df['avg_power_kw'], errors='coerce')
        df['utilization_rate'] = pd.to_numeric(df['utilization_rate'], errors='coerce')
        
        df['fast_charger_ratio'] = df['fast_chargers'] / df['total_stations']
        df['total_power_capacity'] = df['total_stations'] * df['avg_power_kw']
        
        df = df.dropna(subset=['state', 'city', 'total_stations'])
        
        self.charging_stations_clean = df
        return df
    
    def clean_market_metrics(self):
        df = self.market_metrics.copy()
        
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        
        numeric_columns = ['total_population', 'ev_penetration_rate', 'gdp_per_capita', 
                          'gasoline_price', 'charging_infrastructure_score']
        
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['incentives_available'] = df['incentives_available'].astype(bool)
        
        df['ev_vehicles_count'] = df['total_population'] * df['ev_penetration_rate']
        df['market_potential_score'] = (
            df['gdp_per_capita'] / 1000 * 
            df['charging_infrastructure_score'] * 
            (1 + df['incentives_available'].astype(int))
        )
        
        df = df.dropna(subset=['state', 'total_population'])
        
        self.market_metrics_clean = df
        return df
    
    def create_features(self):
        sales_df = self.ev_sales_clean.copy()
        
        monthly_sales = sales_df.groupby(['year', 'month', 'state']).agg({
            'sales_amount': 'sum',
            'revenue': 'sum',
            'market_share': 'mean',
            'battery_capacity': 'mean',
            'price_avg': 'mean'
        }).reset_index()
        
        monthly_sales['month_year'] = pd.to_datetime(monthly_sales[['year', 'month']].assign(day=1))
        
        monthly_sales['sales_growth_pct'] = monthly_sales.groupby('state')['sales_amount'].pct_change() * 100
        monthly_sales['revenue_growth_pct'] = monthly_sales.groupby('state')['revenue'].pct_change() * 100
        
        manufacturer_performance = sales_df.groupby(['manufacturer', 'state']).agg({
            'sales_amount': 'sum',
            'revenue': 'sum',
            'market_share': 'mean'
        }).reset_index()
        
        manufacturer_performance['manufacturer_rank'] = (
            manufacturer_performance.groupby('state')['sales_amount']
            .rank(method='dense', ascending=False)
        )
        
        self.monthly_sales = monthly_sales
        self.manufacturer_performance = manufacturer_performance
        
        return monthly_sales, manufacturer_performance
    
    def merge_datasets(self):
        sales_monthly = self.monthly_sales.copy()
        market_data = self.market_metrics_clean.copy()
        charging_data = self.charging_stations_clean.groupby('state').agg({
            'total_stations': 'sum',
            'fast_chargers': 'sum',
            'slow_chargers': 'sum',
            'avg_power_kw': 'mean',
            'utilization_rate': 'mean',
            'total_power_capacity': 'sum'
        }).reset_index()
        
        merged_data = sales_monthly.merge(
            market_data[['year', 'month', 'state', 'ev_penetration_rate', 'gdp_per_capita', 
                        'gasoline_price', 'incentives_available', 'market_potential_score']],
            on=['year', 'month', 'state'],
            how='left'
        )
        
        merged_data = merged_data.merge(
            charging_data,
            on='state',
            how='left'
        )
        
        merged_data['stations_per_1000_ev'] = (
            merged_data['total_stations'] / (merged_data['sales_amount'] / 1000)
        ).fillna(0)
        
        merged_data['ev_density'] = merged_data['sales_amount'] / merged_data['total_population']
        
        self.merged_data = merged_data
        return merged_data
    
    def save_processed_data(self):
        self.ev_sales_clean.to_csv(
            os.path.join(self.processed_data_path, 'ev_sales_clean.csv'), index=False
        )
        self.charging_stations_clean.to_csv(
            os.path.join(self.processed_data_path, 'charging_stations_clean.csv'), index=False
        )
        self.market_metrics_clean.to_csv(
            os.path.join(self.processed_data_path, 'market_metrics_clean.csv'), index=False
        )
        self.monthly_sales.to_csv(
            os.path.join(self.processed_data_path, 'monthly_sales.csv'), index=False
        )
        self.manufacturer_performance.to_csv(
            os.path.join(self.processed_data_path, 'manufacturer_performance.csv'), index=False
        )
        self.merged_data.to_csv(
            os.path.join(self.processed_data_path, 'merged_analytics_data.csv'), index=False
        )
    
    def generate_summary_stats(self):
        summary = {
            'total_ev_sales': int(self.ev_sales_clean['sales_amount'].sum()),
            'total_revenue': float(self.ev_sales_clean['revenue'].sum()),
            'unique_states': int(self.ev_sales_clean['state'].nunique()),
            'unique_manufacturers': int(self.ev_sales_clean['manufacturer'].nunique()),
            'date_range': {
                'start': self.ev_sales_clean['date'].min().strftime('%Y-%m-%d'),
                'end': self.ev_sales_clean['date'].max().strftime('%Y-%m-%d')
            },
            'total_charging_stations': int(self.charging_stations_clean['total_stations'].sum()),
            'avg_penetration_rate': float(self.market_metrics_clean['ev_penetration_rate'].mean())
        }
        
        import json
        with open(os.path.join(self.processed_data_path, 'data_summary.json'), 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def process_all(self):
        print("Loading raw data...")
        self.load_data()
        
        print("Cleaning EV sales data...")
        self.clean_ev_sales()
        
        print("Cleaning charging stations data...")
        self.clean_charging_stations()
        
        print("Cleaning market metrics data...")
        self.clean_market_metrics()
        
        print("Creating features...")
        self.create_features()
        
        print("Merging datasets...")
        self.merge_datasets()
        
        print("Saving processed data...")
        self.save_processed_data()
        
        print("Generating summary statistics...")
        summary = self.generate_summary_stats()
        
        print("Data processing completed successfully!")
        print(f"Processed {summary['total_ev_sales']} EV sales records")
        print(f"Total revenue: ${summary['total_revenue']:,.2f}")
        print(f"Coverage: {summary['unique_states']} states, {summary['unique_manufacturers']} manufacturers")
        
        return summary

if __name__ == "__main__":
    processor = EVDataProcessor()
    processor.process_all()
