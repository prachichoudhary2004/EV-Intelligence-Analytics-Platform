from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from config.config import config
from services.kpi_engine import kpi_engine
from models.forecaster import forecaster
import uvicorn

app = FastAPI(title="Enterprise EV Market Intelligence API", version="1.0.0")

# Cache for our gold data - acts like a simple database
def load_gold_data():
    try:
        return pd.read_parquet(config.GOLD_DIR / "master_analytics_gold.parquet")
    except:
        return None

@app.get("/")
def read_root():
    return {"message": "Welcome to the EV Market Intelligence API", "status": "Online"}

@app.get("/kpis/market")
def get_market_kpis():
    df = load_gold_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Data not found. Run ETL pipeline first.")
    
    kpis = kpi_engine.get_market_kpis(df)
    return kpis

@app.get("/analytics/benchmarks")
def get_benchmarks():
    df = load_gold_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Data not found.")
    
    benchmarks = kpi_engine.benchmark_states(df)
    return benchmarks.to_dict(orient="records")

@app.get("/forecast/prophet")
def get_forecast(periods: int = 12):
    df = load_gold_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Data not found.")
    
    forecast_df = forecaster.forecast_prophet(df, periods=periods)
    # Need to convert dates to strings so JSON can handle them
    forecast_df['ds'] = forecast_df['ds'].dt.strftime('%Y-%m-%d')
    return forecast_df.to_dict(orient="records")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
