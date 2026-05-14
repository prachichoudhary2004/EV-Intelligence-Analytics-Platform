import pandas as pd
import numpy as np
from utils.logger import logger


class KPIEngine:
    @staticmethod
    def calculate_cagr(start_value, end_value, periods):
        if start_value <= 0 or periods <= 0:
            return 0.0
        return (pow((end_value / start_value), (1 / periods)) - 1) * 100

    @staticmethod
    def calculate_yoy_growth(current_df, date_col="date", value_col="sales_amount"):
        df = current_df.copy()
        df = df.sort_values(date_col)
        df["last_year"] = df[value_col].shift(12)
        df["yoy_growth"] = ((df[value_col] - df["last_year"]) / df["last_year"]) * 100
        return df

    def get_market_kpis(self, df: pd.DataFrame):
        logger.info("Computing India market KPIs...")
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        latest_date = df["date"].max()
        prev_year_date = latest_date - pd.DateOffset(years=1)

        latest_metrics = df[df["date"] == latest_date]
        prev_year_metrics = df[df["date"] == prev_year_date]

        if latest_metrics.empty:
            raise ValueError("No rows for latest date — run ETL.")

        # If YoY anchor month missing (e.g. irregular calendar), pick closest prior month
        if prev_year_metrics.empty:
            eligible = df["date"] <= prev_year_date
            if eligible.any():
                prev_year_date = df.loc[eligible, "date"].max()
                prev_year_metrics = df[df["date"] == prev_year_date]

        total_sales = float(latest_metrics["sales_amount"].sum())
        prev_sales = float(prev_year_metrics["sales_amount"].sum()) if not prev_year_metrics.empty else 0.0
        yoy_growth = ((total_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0.0

        # Master grain repeats state-level columns per OEM/segment — aggregate first
        state_latest = latest_metrics.groupby("state", as_index=False).agg(
            ev_penetration_rate=("ev_penetration_rate", "mean"),
            total_stations=("total_stations", "max"),
        )
        avg_pen = float(state_latest["ev_penetration_rate"].mean())
        total_stations_unique = float(state_latest["total_stations"].sum())

        tier = "Leaders vs laggards widening" if avg_pen > 0.085 else "Mostly early-stage adoption"

        raw_infra = (
            round(total_stations_unique / (total_sales / 1000), 2) if total_sales > 0 else 0.0
        )
        # Thin latest months (esp. after resampling) can blow this ratio up — cap for display sanity
        infra_score = float(min(raw_infra, 250.0))

        kpis = {
            "total_sales": total_sales,
            "yoy_growth": round(yoy_growth, 2),
            "avg_penetration": round(avg_pen * 100, 2),
            "total_revenue": float(latest_metrics["revenue"].sum()),
            "infrastructure_score": infra_score,
            "market_maturity": tier,
        }
        return kpis

    def benchmark_states(self, df: pd.DataFrame):
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        latest_date = df["date"].max()
        latest_df = df[df["date"] == latest_date]

        # One row per state (avoid ranking duplicates from OEM×segment grain)
        state_latest = (
            latest_df.groupby("state", as_index=False)["ev_penetration_rate"].mean()
        )
        national_avg = float(state_latest["ev_penetration_rate"].mean())
        state_latest = state_latest.assign(
            vs_national_avg=(
                (state_latest["ev_penetration_rate"] - national_avg)
                / max(national_avg, 1e-9)
                * 100
            )
        )
        return state_latest[["state", "ev_penetration_rate", "vs_national_avg"]]

    def two_vs_four_split(self, df: pd.DataFrame) -> dict:
        """Calculates the 2W vs 4W mix based on the latest month."""
        if "vehicle_segment" not in df.columns:
            return {"2W": 0.5, "4W": 0.5}
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        latest_date = df["date"].max()
        latest = df[df["date"] == latest_date]
        s = latest.groupby("vehicle_segment")["sales_amount"].sum()
        total = float(s.sum()) or 1.0
        return {k: round(float(s.get(k, 0)) / total, 3) for k in ("2W", "4W")}

    @staticmethod
    def state_sales_cagr(df: pd.DataFrame, state: str, months: int = 12) -> float:
        d = (
            df[df["state"] == state]
            .groupby("date", as_index=False)["sales_amount"]
            .sum()
            .sort_values("date")
        )
        if len(d) < months + 1:
            return 0.0
        start = d["sales_amount"].iloc[-(months + 1)]
        end = d["sales_amount"].iloc[-1]
        if start <= 0:
            return 0.0
        return round((pow(end / start, 12 / months) - 1) * 100, 2)


kpi_engine = KPIEngine()
