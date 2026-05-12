import pandas as pd
from utils.logger import logger

class InsightEngine:
    """
    Executive Narrative Engine for automated business summaries and recommendations.
    """
    
    def generate_executive_summary(self, kpis, top_states):
        """Generate a natural language summary of the market status."""
        logger.info("Generating Executive Narrative...")
        
        status = "positive" if kpis['yoy_growth'] > 10 else "stable"
        
        narrative = f"""
        ### Executive Market Intelligence Summary
        
        The EV Market is currently in a **{kpis['market_maturity']}** phase, showing a **{kpis['yoy_growth']}% YoY growth** in sales volume. 
        Current market penetration stands at **{kpis['avg_penetration']}%**, driven primarily by infrastructure expansions in key regions.
        
        **Key Highlights:**
        * **Top Performer:** {top_states.iloc[0]['state']} leads the market with the highest adoption efficiency.
        * **Infrastructure:** The current ratio of {kpis['infrastructure_score']} stations per 1k EVs suggests a {'healthy' if kpis['infrastructure_score'] > 5 else 'strained'} support network.
        * **Revenue Outlook:** Total market revenue has reached ${kpis['total_revenue']:,.2f} in the latest period.
        
        **Strategic Recommendation:**
        Focus expansion efforts on {top_states.iloc[1]['state']} and {top_states.iloc[2]['state']} where infrastructure utilization is peaking, indicating high latent demand.
        """
        return narrative

    def detect_anomalies(self, df):
        """Simple rule-based anomaly detection for alerts."""
        latest_sales = df.groupby('state')['sales_amount'].last()
        avg_sales = df.groupby('state')['sales_amount'].mean()
        
        alerts = []
        for state, sales in latest_sales.items():
            if sales > avg_sales[state] * 2:
                alerts.append(f"🚀 SURGE: {state} is performing 100% above historical average.")
            elif sales < avg_sales[state] * 0.5:
                alerts.append(f"⚠️ DROP: {state} sales have fallen 50% below average.")
                
        return alerts

# Global instance
insight_engine = InsightEngine()
