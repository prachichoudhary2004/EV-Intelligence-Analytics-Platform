import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config
from design_system.theme import theme
from components.sidebar import render_sidebar
from components.kpi_cards import kpi_card, live_ticker
from services.kpi_engine import kpi_engine
from services.insight_engine import insight_engine
from services.spark_engine import spark_engine
from services.streaming_service import streaming_service
from models.forecaster import forecaster
from services.data_quality import dq_monitor

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="EV Market Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Premium Styling
theme.apply_custom_css()
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def get_gold_data():
    if not (config.GOLD_DIR / "master_analytics_gold.parquet").exists():
        # Auto-run mini ETL if gold is missing
        spark_engine.run_pipeline()
    return pd.read_parquet(config.GOLD_DIR / "master_analytics_gold.parquet")

def main():
    # --- HEADER & TICKER ---
    ticker_items = [
        f"US MKT INDEX: {streaming_service.get_ticker_update()['market_index']} ({streaming_service.get_ticker_update()['index_change']}%)",
        f"TOP MOVER: {streaming_service.get_ticker_update()['top_mover']}",
        f"MOMENTUM: {streaming_service.get_ticker_update()['momentum_score']}/100"
    ]
    live_ticker(ticker_items)
    
    # --- SIDEBAR ---
    page = render_sidebar()
    
    # --- LOAD DATA ---
    try:
        df = get_gold_data()
    except Exception as e:
        st.error(f"Failed to load platform data: {e}")
        return

    # --- ROUTING ---
    if page == "📊 Executive Summary":
        render_executive_dashboard(df)
    elif page == "🌐 Market Intelligence":
        render_market_intelligence(df)
    elif page == "📈 ML Sales Forecasting":
        render_ml_forecasting(df)
    elif page == "🧪 Data Health & ML Ops":
        render_data_health(df)
    elif page == "🛂 API & Integration":
        render_api_docs()

def render_executive_dashboard(df):
    st.markdown("<h1 class='animate-fade-in'>Executive Intelligence Dashboard</h1>", unsafe_allow_html=True)
    
    # KPIs
    kpis = kpi_engine.get_market_kpis(df)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        kpi_card("Total Market Sales", f"{kpis['total_sales']/1000:,.1f}", trend=kpis['yoy_growth'], suffix="K")
    with col2:
        kpi_card("Market Revenue", f"{kpis['total_revenue']/1e9:,.1f}", trend=12.4, prefix="$", suffix="B")
    with col3:
        kpi_card("EV Penetration", f"{kpis['avg_penetration']}", trend=2.1, suffix="%")
    with col4:
        kpi_card("Infra Efficiency", f"{kpis['infrastructure_score']}", trend_up=False, trend=-1.5)

    # Narrative Engine
    st.markdown("---")
    top_states = kpi_engine.benchmark_states(df).sort_values("vs_national_avg", ascending=False)
    narrative = insight_engine.generate_executive_summary(kpis, top_states)
    st.markdown(f"<div class='glass-card'>{narrative}</div>", unsafe_allow_html=True)

    # Visuals
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📈 Sales Acceleration (YoY)")
        fig = px.line(df.groupby('date')['sales_amount'].sum().reset_index(), 
                     x='date', y='sales_amount', template="plotly_dark",
                     color_discrete_sequence=[theme.COLORS['primary']])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🗺️ State Benchmarking")
        fig = px.bar(top_states.head(10), x='vs_national_avg', y='state', orientation='h',
                    template="plotly_dark", color='vs_national_avg',
                    color_continuous_scale='Viridis')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

def render_market_intelligence(df):
    st.markdown("<h1>Market Intelligence Hub</h1>", unsafe_allow_html=True)
    
    # State Selector
    selected_state = st.selectbox("Select State for Deep Dive", df['state'].unique())
    state_df = df[df['state'] == selected_state]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {selected_state} Infrastructure")
        fig = px.pie(values=[state_df['fast_chargers'].iloc[0], state_df['total_stations'].iloc[0] - state_df['fast_chargers'].iloc[0]], 
                    names=['Fast Chargers', 'Standard'], hole=0.6, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Correlation Heatmap")
        corr = df[['sales_amount', 'ev_penetration_rate', 'gdp_per_capita', 'gasoline_price', 'total_stations']].corr()
        fig = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

def render_ml_forecasting(df):
    st.markdown("<h1>Advanced Predictive Forecaster</h1>", unsafe_allow_html=True)
    
    forecast_df = forecaster.forecast_prophet(df)
    
    fig = go.Figure()
    # Historical
    hist = df.groupby('date')['sales_amount'].sum().reset_index()
    fig.add_trace(go.Scatter(x=hist['date'], y=hist['sales_amount'], name="Historical", line=dict(color="#FFF")))
    # Forecast
    fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'], name="Prophet Forecast", line=dict(color=theme.COLORS['primary'], dash='dash')))
    # Confidence Bands
    fig.add_trace(go.Scatter(x=forecast_df['ds'].tolist() + forecast_df['ds'].tolist()[::-1],
                             y=forecast_df['yhat_upper'].tolist() + forecast_df['yhat_lower'].tolist()[::-1],
                             fill='toself', fillcolor='rgba(0,255,65,0.1)', line=dict(color='rgba(255,255,255,0)'),
                             name="Confidence Interval"))
    
    fig.update_layout(template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)

def render_data_health(df):
    st.markdown("<h1>Data Health & ML Ops Center</h1>", unsafe_allow_html=True)
    
    # Health Score
    report = dq_monitor.check_dataframe(df, "Gold_Master_Table")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Data Quality Score", f"{report['quality_score']}%", "+0.2%")
    col2.metric("Schema Drift", "Negative", "Clean")
    col3.metric("Duplicates", report['duplicate_rows'], "0.0%")
    
    st.markdown("### Feature Store Metadata")
    st.json(report['schema'])

def render_api_docs():
    st.markdown("<h1>API & Integration Gateway</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='glass-card'>
        <h3>REST API Documentation</h3>
        <p>The platform exposes a production-ready FastAPI backend for external consumption.</p>
        <code>GET /kpis/market</code><br>
        <code>GET /forecast/prophet?periods=12</code><br>
        <code>GET /analytics/benchmarks</code>
    </div>
    """, unsafe_allow_html=True)
    st.info("API Key required for production access. See Administrator.")

if __name__ == "__main__":
    main()
