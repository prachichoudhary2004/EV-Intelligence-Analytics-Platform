from fastapi import FastAPI, HTTPException
import numpy as np
import pandas as pd
from config.config import config
from services.kpi_engine import kpi_engine
from models.forecaster import forecaster
import uvicorn

app = FastAPI(
    title="India EV Market Intelligence API",
    description="JSON endpoints over the local gold Parquet layer (demo / portfolio use).",
    version="1.1.0",
)


def load_gold_data():
    try:
        return pd.read_parquet(config.GOLD_DIR / "master_analytics_gold.parquet")
    except Exception:
        return None


@app.get("/")
def read_root():
    return {
        "service": "India EV Market Intelligence API",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/kpis/market")
def get_market_kpis():
    df = load_gold_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Gold data missing. Run ETL after bronze refresh.")
    kpis = kpi_engine.get_market_kpis(df)
    return {k: (v.item() if isinstance(v, np.generic) else v) for k, v in kpis.items()}


@app.get("/analytics/benchmarks")
def get_benchmarks():
    df = load_gold_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Gold data missing.")
    return kpi_engine.benchmark_states(df).to_dict(orient="records")


@app.get("/states")
def get_states():
    df = load_gold_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Gold data missing.")
    states = df["state"].unique().tolist()
    return {"states": states}


@app.get("/manufacturers")
def get_manufacturers():
    df = load_gold_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Gold data missing.")
    manufacturers = df["manufacturer"].unique().tolist()
    return {"manufacturers": manufacturers}


@app.get("/market-insights")
def get_market_insights():
    df = load_gold_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Gold data missing.")
    kpis = kpi_engine.get_market_kpis(df)
    # Convert numpy types to native python for JSON
    return {k: (v.item() if hasattr(v, "item") else v) for k, v in kpis.items()}


@app.get("/forecast/prophet")
def get_forecast(periods: int = 12):
    df = load_gold_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Gold data missing.")
    forecast_df = forecaster.forecast_prophet(df, periods=periods)
    out = forecast_df.copy()
    out["ds"] = pd.to_datetime(out["ds"]).dt.strftime("%Y-%m-%d")
    return out.to_dict(orient="records")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
