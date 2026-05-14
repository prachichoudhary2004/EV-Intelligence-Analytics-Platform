import pandas as pd
from utils.logger import logger


class InsightEngine:
    """Short analyst-style notes — written to read like an internal BI commentary."""

    def generate_executive_summary(self, kpis: dict, top_states: pd.DataFrame) -> str:
        logger.info("Generating executive commentary...")
        if top_states.empty or len(top_states) < 2:
            return "Not enough state-level rows in the latest month to write a useful commentary."

        s1 = top_states.iloc[0]["state"]
        s2 = top_states.iloc[1]["state"]
        s3 = top_states.iloc[2]["state"] if len(top_states) > 2 else s2

        yoy = kpis.get("yoy_growth", 0)
        pen = kpis.get("avg_penetration", 0)
        infra = kpis.get("infrastructure_score", 0)
        rev_bn = float(kpis.get("total_revenue", 0)) / 1e9

        if yoy >= 12:
            pace = "Volumes are moving up at a brisk clip year-on-year."
        elif yoy >= 4:
            pace = "Growth is positive, but not uniform across states."
        else:
            pace = "Growth has cooled versus last year — worth checking policy and supply-side constraints."

        # infrastructure_score = total public chargers (state roll-up) / units sold (thousands) in latest month
        if infra >= 35:
            infra_note = "On this sample, charger counts per 1,000 units look high in the aggregate — sanity-check joins before quoting externally."
        elif infra >= 12:
            infra_note = "Charger density is middling: fine for early fleets, but peak-hour queues will show up fast if 4W share rises without new fast hubs."
        else:
            infra_note = "Public charging still looks thin versus sales run-rate — expect adoption to slow first in highway + apartment use-cases."

        return f"""
<div class="glass-card">

<strong>What changed</strong><br/>
{pace} Penetration in the latest month is about <strong>{pen:.1f}%</strong> on this synthetic India sample (not a government statistic).

<strong>Where demand clusters</strong><br/>
<strong>{s1}</strong>, <strong>{s2}</strong>, and <strong>{s3}</strong> are ahead of the national penetration baseline. That usually lines up with a mix of state subsidy design, better charger coverage in metros, and stronger retail networks for 2W/4W EVs.

<strong>Revenue (modelled)</strong><br/>
Indicative revenue stack in the latest month is about <strong>{rev_bn:.2f}</strong> on an internal billion-scale index (joins + synthetic price bands — not audited financials).

<strong>Infrastructure</strong><br/>
{infra_note}

<strong>What I would watch next</strong><br/>
State-wise fast-charger share, 2W vs 4W mix shifts, and whether incentives are translating into sustained retail throughput (not just showroom spikes).

</div>
""".strip()

    def detect_anomalies(self, df: pd.DataFrame):
        latest_sales = df.groupby("state")["sales_amount"].last()
        avg_sales = df.groupby("state")["sales_amount"].mean()
        alerts = []
        for state, sales in latest_sales.items():
            if sales > avg_sales[state] * 2:
                alerts.append(f"{state}: latest month is unusually high vs its own history.")
            elif sales < avg_sales[state] * 0.5:
                alerts.append(f"{state}: latest month looks soft vs its usual run-rate.")
        return alerts


insight_engine = InsightEngine()
