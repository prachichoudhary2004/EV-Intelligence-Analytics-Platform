import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .chart_style import SERIES, style_plotly

def india_choropleth_sales(state_perf_df: pd.DataFrame):
    """
    Renders an India choropleth map. 
    Note: Requires GeoJSON for India states. If unavailable, returns None to fallback.
    """
    # For a portfolio, we usually link to a hosted GeoJSON
    # https://raw.githubusercontent.com/HindustanTimesLabs/shapefiles/master/india_st.json
    return None # Fallback to bar chart in app.py logic

def top_states_bar(state_perf_df: pd.DataFrame):
    """Horizontal bar chart for state rankings."""
    df = state_perf_df.sort_values("sales_amount", ascending=True).tail(10)
    fig = px.bar(
        df,
        y="state",
        x="sales_amount",
        orientation="h",
        color="sales_amount",
        color_continuous_scale="Viridis",
        title="Top 10 States by EV Sales"
    )
    fig.update_layout(showlegend=False)
    return style_plotly(fig)
