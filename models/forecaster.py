"""Forecasting: Prophet for trend forecasts; optional XGBoost training."""

from __future__ import annotations

import os
import sys

import joblib
import pandas as pd
from sklearn.metrics import r2_score
from xgboost import XGBRegressor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prophet import Prophet

from config.config import config
from utils.logger import logger


class EVForecaster:
    """
    Prophet for series forecasts; XGBoost for tabular short-horizon experiments.
    """

    feature_cols = ["year", "month", "ev_penetration_rate", "gdp_per_capita", "total_stations"]

    def __init__(self) -> None:
        self.xgb_model = XGBRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            random_state=config.RANDOM_STATE,
        )
        self.prophet_model: Prophet | None = None

    @staticmethod
    def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["date"] = pd.to_datetime(out["date"], errors="coerce")
        out["year"] = out["date"].dt.year
        out["month"] = out["date"].dt.month
        return out

    def train_xgboost(self, df: pd.DataFrame) -> float:
        logger.info("Training XGBoost Regressor...")
        prepared = self.prepare_features(df)
        train = prepared.sample(frac=0.8, random_state=config.RANDOM_STATE)
        test = prepared.drop(train.index)

        X_train = train[self.feature_cols]
        y_train = train["sales_amount"]
        X_test = test[self.feature_cols]
        y_test = test["sales_amount"]

        self.xgb_model.fit(X_train, y_train)
        preds = self.xgb_model.predict(X_test)
        r2 = float(r2_score(y_test, preds))
        logger.info("XGBoost R2 Score: %.4f", r2)

        config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.xgb_model, config.MODEL_DIR / "xgb_forecaster.pkl")
        return r2

    def forecast_prophet(self, df: pd.DataFrame, periods: int = 12) -> pd.DataFrame:
        if periods <= 0:
            raise ValueError("periods must be a positive integer.")

        work = df.copy()
        work["date"] = pd.to_datetime(work["date"], errors="coerce")
        work["sales_amount"] = pd.to_numeric(work["sales_amount"], errors="coerce")
        work = work.dropna(subset=["date", "sales_amount"])
        if work.empty:
            raise ValueError("No valid rows for Prophet forecast.")

        # Month-start totals: stable for Prophet and faster than daily national sums.
        prophet_df = (
            work.groupby(pd.Grouper(key="date", freq="MS"))["sales_amount"]
            .sum()
            .reset_index()
            .rename(columns={"date": "ds", "sales_amount": "y"})
            .sort_values("ds")
        )

        logger.info("Generating Prophet time-series forecast...")
        self.prophet_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
        )
        self.prophet_model.fit(prophet_df)

        future = self.prophet_model.make_future_dataframe(periods=periods, freq="MS")
        forecast = self.prophet_model.predict(future)

        config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.prophet_model, config.MODEL_DIR / "prophet_model.pkl")

        return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

    @staticmethod
    def run_scenario_simulation(df: pd.DataFrame, growth_multiplier: float = 1.2) -> float:
        logger.info("Running scenario simulation: %sx growth", growth_multiplier)
        series = df.copy()
        series["date"] = pd.to_datetime(series["date"], errors="coerce")
        series["sales_amount"] = pd.to_numeric(series["sales_amount"], errors="coerce")
        last_sales = series.groupby("date")["sales_amount"].sum().iloc[-1]
        return float(last_sales * growth_multiplier)


forecaster = EVForecaster()

if __name__ == "__main__":
    gold = pd.read_parquet(config.GOLD_DIR / "master_analytics_gold.parquet")
    forecaster.train_xgboost(gold)
    forecaster.forecast_prophet(gold)
    print("ML model training complete.")
