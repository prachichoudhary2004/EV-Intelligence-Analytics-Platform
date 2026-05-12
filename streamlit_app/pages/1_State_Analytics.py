import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add parent so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="State Analytics - EV Intelligence",
    page_icon="🗺️",
    layout="wide"
)

# Make it look nice
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    .metric-card {
        background-color: #1E2139;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #00FF41;
    }
    .insight-card {
        background-color: #1E2139;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #2A2D3A;
    }
    h1, h2, h3 {
        color: #00FF41;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    ev_sales = pd.read_csv('../data/processed/ev_sales_clean.csv')
    charging_stations = pd.read_csv('../data/processed/charging_stations_clean.csv')
    market_metrics = pd.read_csv('../data/processed/market_metrics_clean.csv')
    merged_data = pd.read_csv('../data/processed/merged_analytics_data.csv')
    
    ev_sales['date'] = pd.to_datetime(ev_sales['date'])
    market_metrics['date'] = pd.to_datetime(market_metrics['date'])
    merged_data['date'] = pd.to_datetime(merged_data['date'])
    
    return {
        'ev_sales': ev_sales,
        'charging_stations': charging_stations,
        'market_metrics': market_metrics,
        'merged_data': merged_data
    }

def main():
    data = load_data()
    
    st.markdown("# 🗺️ State Performance Analytics")
    st.markdown("---")
    
    # State selection
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_state = st.selectbox(
            "Select State for Analysis",
            sorted(data['ev_sales']['state'].unique())
        )
    
    with col2:
        comparison_mode = st.checkbox("Compare States")
    
    with col3:
        if comparison_mode:
            comparison_states = st.multiselect(
                "Select Comparison States",
                sorted(data['ev_sales']['state'].unique()),
                default=[]
            )
    
    # State overview
    state_data = data['ev_sales'][data['ev_sales']['state'] == selected_state]
    state_metrics = data['market_metrics'][data['market_metrics']['state'] == selected_state]
    state_charging = data['charging_stations'][data['charging_stations']['state'] == selected_state]
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Sales</h3>
            <h2>{state_data['sales_amount'].sum():,}</h2>
            <p>Units Sold</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Revenue</h3>
            <h2>${state_data['revenue'].sum():,.2f}</h2>
            <p>Market Value</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        penetration_rate = state_metrics['ev_penetration_rate'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Penetration Rate</h3>
            <h2>{penetration_rate:.2%}</h2>
            <p>EV Adoption</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_stations = state_charging['total_stations'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Charging Stations</h3>
            <h2>{total_stations:,}</h2>
            <p>Infrastructure</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Time series analysis
    st.markdown("## 📈 Temporal Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly sales trend
        monthly_sales = state_data.groupby(state_data['date'].dt.to_period('M')).agg({
            'sales_amount': 'sum',
            'revenue': 'sum'
        }).reset_index()
        monthly_sales['date'] = monthly_sales['date'].dt.to_timestamp()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Monthly Sales Volume', 'Monthly Revenue'),
            vertical_spacing=0.08
        )
        
        fig.add_trace(
            go.Scatter(
                x=monthly_sales['date'],
                y=monthly_sales['sales_amount'],
                mode='lines+markers',
                name='Sales',
                line=dict(color='#00FF41', width=3)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=monthly_sales['date'],
                y=monthly_sales['revenue'],
                mode='lines+markers',
                name='Revenue',
                line=dict(color='#FF6B6B', width=3)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            template="plotly_dark",
            title_text=f"{selected_state} Monthly Performance"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Market penetration trend
        penetration_trend = state_metrics.groupby('date')['ev_penetration_rate'].mean().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=penetration_trend['date'],
            y=penetration_trend['ev_penetration_rate'],
            mode='lines+markers',
            name='Penetration Rate',
            line=dict(color='#4ECDC4', width=3),
            fill='tonexty'
        ))
        
        fig.update_layout(
            title=f"{selected_state} EV Penetration Trend",
            xaxis_title="Date",
            yaxis_title="Penetration Rate",
            template="plotly_dark",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Manufacturer analysis
    st.markdown("## 🏭 Manufacturer Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Manufacturer market share
        manufacturer_sales = state_data.groupby('manufacturer')['sales_amount'].sum().sort_values(ascending=False)
        
        fig = go.Figure(data=[
            go.Pie(
                labels=manufacturer_sales.index,
                values=manufacturer_sales.values,
                hole=0.3
            )
        ])
        
        fig.update_layout(
            title=f"Manufacturer Market Share in {selected_state}",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Manufacturer performance comparison
        manufacturer_metrics = state_data.groupby('manufacturer').agg({
            'sales_amount': 'sum',
            'price_avg': 'mean',
            'battery_capacity': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=manufacturer_metrics['price_avg'],
            y=manufacturer_metrics['sales_amount'],
            mode='markers+text',
            text=manufacturer_metrics['manufacturer'],
            textposition="top center",
            marker=dict(
                size=manufacturer_metrics['battery_capacity']/5,
                color=manufacturer_metrics['sales_amount'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sales Volume")
            ),
            name='Manufacturers'
        ))
        
        fig.update_layout(
            title="Manufacturer Positioning Map",
            xaxis_title="Average Price",
            yaxis_title="Sales Volume",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Infrastructure analysis
    st.markdown("## ⚡ Charging Infrastructure Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Station utilization
        if not state_charging.empty:
            city_stations = state_charging.groupby('city').agg({
                'total_stations': 'sum',
                'utilization_rate': 'mean',
                'fast_chargers': 'sum',
                'slow_chargers': 'sum'
            }).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=city_stations['city'],
                y=city_stations['utilization_rate'],
                name='Utilization Rate',
                marker_color='#FFD93D'
            ))
            
            fig.update_layout(
                title=f"Charging Station Utilization in {selected_state}",
                xaxis_title="City",
                yaxis_title="Utilization Rate",
                template="plotly_dark",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No charging station data available for this state.")
    
    with col2:
        # Station type distribution
        if not state_charging.empty:
            station_types = pd.DataFrame({
                'Type': ['Fast Chargers', 'Slow Chargers'],
                'Count': [state_charging['fast_chargers'].sum(), state_charging['slow_chargers'].sum()]
            })
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=station_types['Type'],
                    values=station_types['Count'],
                    hole=0.3
                )
            ])
            
            fig.update_layout(
                title=f"Charging Station Types in {selected_state}",
                template="plotly_dark",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # State comparison (if enabled)
    if comparison_mode and comparison_states:
        st.markdown("## 📊 State Comparison Analysis")
        
        comparison_data = data['ev_sales'][data['ev_sales']['state'].isin([selected_state] + comparison_states)]
        
        # Sales comparison
        comparison_sales = comparison_data.groupby(['state', comparison_data['date'].dt.to_period('M')])['sales_amount'].sum().reset_index()
        comparison_sales['date'] = comparison_sales['date'].dt.to_timestamp()
        
        fig = go.Figure()
        
        for state in [selected_state] + comparison_states:
            state_comp_data = comparison_sales[comparison_sales['state'] == state]
            fig.add_trace(go.Scatter(
                x=state_comp_data['date'],
                y=state_comp_data['sales_amount'],
                mode='lines+markers',
                name=state
            ))
        
        fig.update_layout(
            title="Sales Volume Comparison",
            xaxis_title="Date",
            yaxis_title="Sales Amount",
            template="plotly_dark",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # KPI comparison table
        comparison_kpis = []
        for state in [selected_state] + comparison_states:
            state_comp_data = data['ev_sales'][data['ev_sales']['state'] == state]
            state_comp_metrics = data['market_metrics'][data['market_metrics']['state'] == state]
            state_comp_charging = data['charging_stations'][data['charging_stations']['state'] == state]
            
            comparison_kpis.append({
                'State': state,
                'Total Sales': state_comp_data['sales_amount'].sum(),
                'Total Revenue': state_comp_data['revenue'].sum(),
                'Penetration Rate': state_comp_metrics['ev_penetration_rate'].mean(),
                'Charging Stations': state_comp_charging['total_stations'].sum(),
                'Avg Price': state_comp_data['price_avg'].mean()
            })
        
        comparison_df = pd.DataFrame(comparison_kpis)
        st.markdown("### 📋 Comparison Metrics")
        st.dataframe(comparison_df, use_container_width=True)
    
    # State insights
    st.markdown("## 💡 State Insights & Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="insight-card">
            <h4>🎯 Market Position</h4>
            <p><strong>{selected_state}</strong> ranks #{state_data['sales_amount'].sum()} in national sales</p>
            <p>Penetration rate of {penetration_rate:.2%} is {'above' if penetration_rate > 0.05 else 'below'} national average</p>
            <p>Market shows {'strong' if state_data['sales_amount'].sum() > 5000 else 'moderate' if state_data['sales_amount'].sum() > 2000 else 'emerging'} growth potential</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="insight-card">
            <h4>📈 Growth Drivers</h4>
            <p>Top manufacturer: {state_data.groupby('manufacturer')['sales_amount'].sum().idxmax()}</p>
            <p>Popular segment: {state_data.groupby('vehicle_category')['sales_amount'].sum().idxmax()}</p>
            <p>Average price point: ${state_data['price_avg'].mean():,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="insight-card">
            <h4>⚡ Infrastructure Status</h4>
            <p>{total_stations:,} total charging stations</p>
            <p>Station density: {total_stations / (state_data['sales_amount'].sum() / 1000):.1f} per 1000 EVs</p>
            <p>Utilization rate: {state_charging['utilization_rate'].mean():.1%} average</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
