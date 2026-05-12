import streamlit as st

def kpi_card(label, value, trend=None, trend_up=True, prefix="", suffix=""):
    """
    Renders a premium glassmorphism KPI card.
    """
    trend_html = ""
    if trend is not None:
        color = "#00FF41" if trend_up else "#FF6B6B"
        icon = "↑" if trend_up else "↓"
        trend_html = f'<div class="kpi-trend" style="color: {color}">{icon} {trend}% vs LY</div>'
    
    st.markdown(f"""
    <div class="metric-card animate-fade-in">
        <div class="kpi-title">{label}</div>
        <div class="kpi-value">{prefix}{value}{suffix}</div>
        {trend_html}
    </div>
    """, unsafe_allow_html=True)

def live_ticker(data_items):
    """
    Renders a live market ticker.
    """
    ticker_content = "".join([f'<span class="ticker-item">{item}</span>' for item in data_items])
    st.markdown(f"""
    <div class="ticker-container">
        <marquee scrollamount="5">
            {ticker_content}
        </marquee>
    </div>
    """, unsafe_allow_html=True)
