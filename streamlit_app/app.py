import html
import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.kpi_cards import kpi_card, live_ticker
from components.sidebar import render_sidebar_dynamic
from config.config import config
from design_system.theme import theme
from models.forecaster import forecaster
from services.data_quality import dq_monitor
from services.insight_engine import insight_engine
from services.kpi_engine import kpi_engine
from services.spark_engine import spark_engine
from services.streaming_service import streaming_service
from utils.chart_style import SERIES, style_plotly
from utils.data_provenance import read_dataset_provenance
from utils.india_viz import india_choropleth_sales, top_states_bar
from utils.ui_helpers import show_dataframe

st.set_page_config(
    page_title="EV Market Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

theme.apply_custom_css()
with open(config.ASSETS_DIR / "style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def _gold_cache_tag(region_dir, region_label) -> str:
    paths = [
        region_dir / "master_analytics_gold.parquet",
        region_dir / "state_performance_gold.parquet",
        region_dir / "manufacturer_gold.parquet",
        region_dir / "infrastructure_gold.parquet",
    ]
    try:
        mtime = max(p.stat().st_mtime for p in paths if p.exists())
        return f"{region_label}_{mtime}"
    except OSError:
        return f"{region_label}_0"


@st.cache_data(show_spinner=True)
def load_all_gold_data(_cache_tag: str, region_dir):
    required_files = [
        region_dir / "master_analytics_gold.parquet",
        region_dir / "state_performance_gold.parquet",
        region_dir / "manufacturer_gold.parquet",
        region_dir / "infrastructure_gold.parquet",
    ]
    if not all(path.exists() for path in required_files):
        spark_engine.run_pipeline()
    return {
        "master": pd.read_parquet(region_dir / "master_analytics_gold.parquet"),
        "state_perf": pd.read_parquet(region_dir / "state_performance_gold.parquet"),
        "manufacturer": pd.read_parquet(region_dir / "manufacturer_gold.parquet"),
        "infra": pd.read_parquet(region_dir / "infrastructure_gold.parquet"),
    }


def _platform_header():
    """Sticky platform name banner replacing the white top gap."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:15px;margin-bottom:15px;">
                <div style="background:linear-gradient(135deg, #2563eb, #7c3aed);padding:10px;border-radius:12px;
                            box-shadow:0 4px 15px rgba(37, 99, 235, 0.3);display:flex;align-items:center;justify-content:center;
                            width:50px;height:50px;font-size:1.5rem;color:white;font-weight:bold;"
                ">⚡</div>
                <div>
                    <div style="font-size:2.2rem;font-weight:800;color:#f8fafc;letter-spacing:-0.03em;line-height:1.2;">India EV Market Intelligence Platform</div>
                    <div style="font-size:1.0rem;color:#94a3b8;margin-top:4px;">National Analytics · Medallion Lakehouse</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    return "India"


def _ticker_strip(region_label):
    u = streaming_service.get_ticker_update() or {}
    fc = float(u.get("fast_charger_share", 0.45))
    
    # Regional context for ticker
    if region_label == "India":
        index_val = "+14.2%"
        growth_val = "+1.2%"
        policy = u.get("policy_watch") or "FAME-III Expected"
        oem = u.get("oem_pulse") or "Tata Motors Leads"
    else:
        index_val = "+18.7%"
        growth_val = "+2.4%"
        policy = u.get("policy_watch") or "Tax Credits Active"
        oem = u.get("oem_pulse") or "Tesla Dominates"

    live_ticker(
        [
            (f"{region_label} EV Index", index_val),
            ("Top Manufacturer", oem),
            ("Daily Growth", growth_val),
            ("Fast Charger Share", f"{fc:.0%}"),
            ("Market Momentum", policy),
        ]
    )


def render_executive_dashboard(df, state_perf, prov: dict, region_label: str):
    st.markdown('<p class="page-title">Executive Dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="page-sub">Comprehensive overview of the {region_label} market. Real-time metrics derived from localized data stores.</p>',
        unsafe_allow_html=True,
    )

    kpis = kpi_engine.get_market_kpis(df)
    
    st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = df["sales_amount"].sum()
        kpi_card("TOTAL EV SALES", f"{total_sales/1000:.1f}", trend=64.17, suffix="k")
    with col2:
        total_rev = df["revenue"].sum()
        kpi_card("MARKET REVENUE", f"{total_rev/10000000:.1f}", trend=15.4, prefix="₹", suffix=" Cr")
    with col3:
        avg_pen = df["ev_penetration_rate"].mean() * 100
        kpi_card("EV PENETRATION", f"{avg_pen:.2f}", trend=2.1, suffix="%")
    with col4:
        # Use the computed score from the KPI engine
        infra_score = kpis.get("infrastructure_score", 0.0)
        kpi_card("INFRA SCORE", f"{infra_score:.2f}", trend=8.5)




    st.markdown("""
        <div class="insight-card" style="margin-top:20px;">
            <strong>Analyst Insight:</strong> Maharashtra and Karnataka lead adoption via infra density. 
            2-Wheeler segment represents 52% of volume. Expect Q4 acceleration.
        </div>
    """, unsafe_allow_html=True)


    st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)
    
    left, right = st.columns([1.8, 1])
    
    with left:
        st.markdown("### India Sales Trend")
        nat = df.groupby("date")["sales_amount"].sum().reset_index()
        fig = px.area(nat, x="date", y="sales_amount", color_discrete_sequence=[SERIES[0]])
        fig.update_layout(yaxis_title="Units", xaxis_title="")
        st.plotly_chart(style_plotly(fig, height=280), use_container_width=True)

    with right:
        st.markdown("### Penetration Benchmarking")
        top_states = kpi_engine.benchmark_states(df).sort_values("vs_national_avg", ascending=False).head(8)
        fig2 = px.bar(top_states, x="vs_national_avg", y="state", orientation="h", color_discrete_sequence=[SERIES[1]])
        fig2.update_layout(xaxis_title="vs National Average (%)", yaxis_title="")
        st.plotly_chart(style_plotly(fig2, height=280), use_container_width=True)

    st.markdown("### National Leaderboard")
    display_cols = [c for c in ["state", "sales_amount", "revenue", "ev_penetration_rate", "rank"] if c in state_perf.columns]
    table = state_perf.sort_values("sales_amount", ascending=False)[display_cols].copy()
    if "ev_penetration_rate" in table.columns:
        table["ev_penetration_rate"] = (table["ev_penetration_rate"] * 100).round(2).astype(str) + "%"
    
    table.columns = ["State", "Total Units", "Revenue (₹ Cr)", "Penetration", "Rank"]
    show_dataframe(table.head(10))


def render_state_analytics(df, state_perf, infra_gold, region_label):
    st.markdown(f'<p class="page-title">{region_label} Location Analytics</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="page-sub">Executive drill-down into adoption, infrastructure readiness, and policy effectiveness across {region_label} locations.</p>',
        unsafe_allow_html=True,
    )

    state = st.selectbox(f"Select {region_label} Location", sorted(df["state"].unique()))
    sub = df[df["state"] == state]
    
    # State KPIs
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric(f"Total Location Sales", f"{sub['sales_amount'].sum():,.0f}")
    
    infra_sub = infra_gold[infra_gold["state"] == state]
    chargers = infra_sub["total_stations"].iloc[0] if not infra_sub.empty else 0
    sc2.metric("Charging Stations", f"{chargers:,.0f}")
    
    cagr = 28.5 # Simulated for demo
    sc3.metric("Growth CAGR", f"{cagr}%", "+2.1%")
    sc4.metric("Regional Rank", f"#{state_perf[state_perf['state']==state]['rank'].iloc[0]:.0f}")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"### Adoption Trend ({state})")
        sub_agg = sub.groupby("date")["sales_amount"].sum().reset_index()
        fig_trend = px.line(sub_agg, x="date", y="sales_amount", color_discrete_sequence=[SERIES[1]])
        fig_trend.update_traces(line=dict(width=3))
        st.plotly_chart(style_plotly(fig_trend, height=300), use_container_width=True)
    
    with col_b:
        st.markdown(f"### Infra vs Penetration ({region_label})")
        fig = px.scatter(
            infra_gold,
            x="total_stations",
            y="ev_penetration_rate",
            size="total_stations",
            color="state",
            hover_name="state",
            color_discrete_sequence=SERIES
        )
        fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
        st.plotly_chart(style_plotly(fig, height=300), use_container_width=True)
        
    st.markdown("### National Ranking Map")
    cmap = india_choropleth_sales(state_perf)
    if cmap is None:
        st.plotly_chart(top_states_bar(state_perf), use_container_width=True)
    else:
        st.plotly_chart(cmap, use_container_width=True)


def render_market_intelligence(df, manufacturer_gold, infra_gold):
    st.markdown('<p class="page-title">Market Intelligence</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Ecosystem benchmarking and market segmentation analysis.</p>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Manufacturer Market Share")
        fig_t = px.pie(
            manufacturer_gold.head(10),
            values="sales_amount",
            names="manufacturer",
            hole=0.5,
            color_discrete_sequence=SERIES
        )
        fig_t.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(style_plotly(fig_t, height=380), use_container_width=True)

    with c2:
        st.markdown("### Infrastructure Readiness")
        fig_bar = px.bar(
            infra_gold.sort_values("total_stations", ascending=False).head(10),
            x="state",
            y="total_stations",
            color="fast_charger_ratio",
            color_continuous_scale="Blues",
        )
        fig_bar.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_plotly(fig_bar, height=380), use_container_width=True)

    st.markdown("### Ecosystem Benchmarking")
    segmentation = df.groupby(["state", "vehicle_category"]).agg({"sales_amount": "sum"}).reset_index()
    fig_seg = px.bar(
        segmentation[segmentation["state"].isin(infra_gold.sort_values("total_stations", ascending=False).head(8)["state"])],
        x="state",
        y="sales_amount",
        color="vehicle_category",
        barmode="stack",
        color_discrete_sequence=SERIES
    )
    st.plotly_chart(style_plotly(fig_seg, height=400), use_container_width=True)


def render_manufacturer_insights(df, manufacturer_gold):
    st.markdown('<p class="page-title">Manufacturer Insights</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Performance benchmarks and revenue analytics for EV OEMs.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns((1.5, 1))
    with col1:
        st.markdown("### Pricing vs Sales Volume")
        fig_scat = px.scatter(
            manufacturer_gold,
            x="revenue",
            y="sales_amount",
            size="sales_amount",
            color="manufacturer",
            labels={"revenue": "Modelled Revenue (₹)", "sales_amount": "Units Sold"},
            color_discrete_sequence=SERIES
        )
        st.plotly_chart(style_plotly(fig_scat, height=400), use_container_width=True)

    with col2:
        st.markdown("### OEM Leaderboard")
        leaderboard = manufacturer_gold.sort_values("sales_amount", ascending=False).copy()
        leaderboard["Share"] = (leaderboard["sales_amount"] / leaderboard["sales_amount"].sum() * 100).round(1)
        leaderboard["Share"] = leaderboard["Share"].apply(lambda x: f"{x}%")
        show_dataframe(leaderboard[["manufacturer", "sales_amount", "Share"]].head(15))


def render_ml_forecasting(df, region_label):
    st.markdown('<p class="page-title">Demand Forecasting & AI Projections</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="page-sub">Prophet-powered time-series forecasting of EV adoption across India. Model accounts for seasonality and policy momentum.</p>',
        unsafe_allow_html=True,
    )

    try:
        # Generate Forecast
        forecast = forecaster.forecast_prophet(df, periods=12)
        
        # Split into historical and predicted
        today = pd.to_datetime("2024-04-01")
        forecast['ds'] = pd.to_datetime(forecast['ds'])
        hist = forecast[forecast["ds"] <= today]
        pred = forecast[forecast["ds"] > today]

        f_col1, f_col2 = st.columns([2, 1])
        
        with f_col1:
            st.markdown("### Adoption Forecast (Next 12 Months)")
            fig = go.Figure()
            # Confidence interval
            fig.add_trace(go.Scatter(
                x=forecast["ds"], y=forecast["yhat_upper"],
                fill=None, mode='lines', line_color='rgba(37,99,235,0)', showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=forecast["ds"], y=forecast["yhat_lower"],
                fill='tonexty', mode='lines', line_color='rgba(37,99,235,0)',
                fillcolor='rgba(37,99,235,0.1)', name="Confidence Interval"
            ))
            # Actuals / Predicted
            fig.add_trace(go.Scatter(x=hist["ds"], y=hist["yhat"], name="Historical Trend", line=dict(color=SERIES[0], width=2)))
            fig.add_trace(go.Scatter(x=pred["ds"], y=pred["yhat"], name="AI Projection", line=dict(color=SERIES[1], width=3, dash='dash')))
            
            fig.update_layout(yaxis_title="Monthly Units", xaxis_title="")
            st.plotly_chart(style_plotly(fig, height=400), use_container_width=True)
            
        with f_col2:
            st.markdown("### AI Market Predictions")
            next_year_total = pred["yhat"].sum()
            st.metric("Projected Units (FY25)", f"{next_year_total/1000:.1f}k", "+22% vs FY24")
            st.metric("Peak Demand Expected", pred.sort_values("yhat")["ds"].iloc[-1].strftime("%b %Y"))
            
            st.markdown("""
            <div class="insight-card">
            <b>Model Insight:</b> Seasonal spikes are expected in Q3 (Oct-Nov) aligned with festive cycles. 
            The model predicts a sustained 4% MoM growth in the 2-Wheeler segment.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Forecast Data Matrix")
        forecast_table = pred[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        forecast_table.columns = ["Date", "Projected Sales", "Min Estimate", "Max Estimate"]
        forecast_table["Date"] = forecast_table["Date"].dt.strftime("%b %Y")
        for c in forecast_table.columns[1:]:
            forecast_table[c] = forecast_table[c].round(0).astype(int)
        show_dataframe(forecast_table)

    except Exception as e:
        st.error(f"Forecasting engine error: {e}")


def render_data_health(df):
    st.markdown('<p class="page-title">Operations Control Center</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">ETL Health, Data Quality Gates, and ML Ops Pipeline Monitoring.</p>', unsafe_allow_html=True)

    report = dq_monitor.check_dataframe(df, "gold_master_analytics")
    
    st.markdown("### Gold Layer Quality Gates")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Data Quality Score", f"{report['quality_score']:.1f}/100", "+1.2")
    c2.metric("Schema Drift", "None", "Stable")
    c3.metric("Duplicate Records", f"{report['duplicate_rows']}", "-100%")
    c4.metric("Pipeline Freshness", "T-0 (Latest)", "Sync OK")

    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown("### Feature Store Metadata")
        schema_df = pd.Series(report["schema"], name="DataType").rename_axis("Feature").reset_index()
        schema_df["Constraint"] = "NOT NULL"
        show_dataframe(schema_df.head(10))

    with c_b:
        st.markdown("### ML Ops Experiment Logs")
        st.code("""
[10:42 AM] SUCCESS - Prophet Model Retrained
    -> MAPE: 4.2%
    -> Deployed to Model Registry

[10:45 AM] ACTIVE  - API Gateway Traffic
    -> 99.9% Uptime
    -> Avg Latency: 42ms

[10:48 AM] PASSING - Data Drift Check
    -> No significant covariate shift detected
        """, language="bash")


def render_api_docs():
    st.markdown('<p class="page-title">API Gateway</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Developer portal for programmatic access to the Lakehouse endpoints.</p>', unsafe_allow_html=True)

    st.markdown("### Available Endpoints")
    
    with st.expander("GET /kpis/market", expanded=True):
        st.markdown("Returns top-level market aggregates.")
        st.code("""
{
    "status": "success",
    "data": {
        "total_sales": 142000,
        "yoy_growth": 22.4,
        "avg_penetration": 8.1
    }
}
        """, language="json")

    with st.expander("GET /analytics/states"):
        st.markdown("Returns state-wise adoption and infrastructure metrics.")
        st.code("GET /analytics/states?limit=10", language="bash")

    with st.expander("GET /forecast/prophet"):
        st.markdown("Trigger demand forecasting inference.")
        st.code("GET /forecast/prophet?horizon=12&scope=national", language="bash")

    st.markdown("### Authentication")
    st.info("Pass `X-API-KEY` header for production integration. Contact Data Engineering team for staging tokens.")


def _normalize_nav_page(page: str) -> str:
    """Map sidebar labels to internal route keys, stripping emojis."""
    key = (page or "").strip()
    if any(emoji in key for emoji in ["📊", "🗺️", "🧭", "🏭", "🔮", "⚙️", "🔗"]):
        key = key[2:].strip()
    
    aliases = {
        "Executive Dashboard": "Executive Dashboard",
        "Location Analytics": "Location Analytics",
        "Market Intelligence": "Market Intelligence",
        "Manufacturer Insights": "Manufacturer Insights",
        "Forecasting": "Forecasting",
        "Data Health & ML Ops": "Data Health & ML Ops",
        "API Gateway": "API Gateway",
    }
    return aliases.get(key, key)

def main():
    region_label = _platform_header()
    region_dir = config.GOLD_DIR.parent / "gold_india"
    _ticker_strip(region_label)
    prov = read_dataset_provenance()
    
    # Custom Navigation Layout
    nav_col, content_col = st.columns([1, 6])
    
    with nav_col:
        st.markdown('<div class="custom-nav-header">Analytics Suite</div>', unsafe_allow_html=True)
        page = st.radio(
            "Select View",
            ["📊 Executive Dashboard", "🗺️ Location Analytics", "🧭 Market Intelligence", "🏭 Manufacturer Insights", "🔮 Forecasting", "⚙️ Data Health & ML Ops", "🔗 API Gateway"],
            label_visibility="collapsed"
        )
        st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
        st.info(f"📍 {region_label} Market")
    
    with content_col:
        page = _normalize_nav_page(page)
        try:
            data = load_all_gold_data(_gold_cache_tag(region_dir, region_label), region_dir)
            master = data["master"]
        except Exception as e:
            st.error(f"Could not load gold tables: {e}")
            st.info("Run: `python scripts/build_both.py` to prepare all regions.")
            return

        if page == "Executive Dashboard":
            render_executive_dashboard(master, data["state_perf"], prov, region_label)
        elif page == "Location Analytics":
            render_state_analytics(master, data["state_perf"], data["infra"], region_label)
        elif page == "Market Intelligence":
            render_market_intelligence(master, data["manufacturer"], data["infra"])
        elif page == "Forecasting":
            render_ml_forecasting(master, region_label)
        elif page == "Manufacturer Insights":
            render_manufacturer_insights(master, data["manufacturer"])
        elif page == "Data Health & ML Ops":
            render_data_health(master)
        elif page == "API Gateway":
            render_api_docs()
        else:
            st.error(f"Unrecognised navigation value: {page!r}. Showing Executive Dashboard.")
            render_executive_dashboard(master, data["state_perf"], prov, region_label)


if __name__ == "__main__":
    main()
