import pandas as pd
import numpy as np
from utils.logger import logger

class KPIEngine:
    """
    Semantic layer for centralized KPI definitions and business logic.
    """
    
    @staticmethod
    def calculate_cagr(start_value, end_value, periods):
        """Calculate Compound Annual Growth Rate."""
        if start_value <= 0 or periods <= 0:
            return 0
        return (pow((end_value / start_value), (1 / periods)) - 1) * 100

    @staticmethod
    def calculate_yoy_growth(current_df, date_col='date', value_col='sales_amount'):
        """Calculate Year-over-Year growth."""
        df = current_df.copy()
        df = df.sort_values(date_col)
        df['last_year'] = df[value_col].shift(12)
        df['yoy_growth'] = ((df[value_col] - df['last_year']) / df['last_year']) * 100
        return df

    def get_market_kpis(self, df):
        """Generate a suite of market-level KPIs."""
        logger.info("Generating Market KPIs...")
        
        latest_date = df['date'].max()
        prev_year_date = latest_date - pd.DateOffset(years=1)
        
        latest_metrics = df[df['date'] == latest_date]
        prev_year_metrics = df[df['date'] == prev_year_date]
        
        total_sales = latest_metrics['sales_amount'].sum()
        prev_sales = prev_year_metrics['sales_amount'].sum()
        
        yoy_growth = ((total_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
        
        kpis = {
            "total_sales": total_sales,
            "yoy_growth": round(yoy_growth, 2),
            "avg_penetration": round(latest_metrics['ev_penetration_rate'].mean() * 100, 2),
            "total_revenue": latest_metrics['revenue'].sum(),
            "infrastructure_score": round(latest_metrics['total_stations'].sum() / (total_sales / 1000) if total_sales > 0 else 0, 2),
            "market_maturity": "Mature" if latest_metrics['ev_penetration_rate'].mean() > 0.08 else "Growth"
        }
        
        return kpis

    def benchmark_states(self, df):
        """Compare states against national averages."""
        latest_date = df['date'].max()
        latest_df = df[df['date'] == latest_date]
        
        national_avg_penetration = latest_df['ev_penetration_rate'].mean()
        
        benchmarks = latest_df.copy()
        benchmarks['vs_national_avg'] = (benchmarks['ev_penetration_rate'] - national_avg_penetration) / national_avg_penetration * 100
        
        return benchmarks[['state', 'ev_penetration_rate', 'vs_national_avg']]

# Global instance
kpi_engine = KPIEngine()
