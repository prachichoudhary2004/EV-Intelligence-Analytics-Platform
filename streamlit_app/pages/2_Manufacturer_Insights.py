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
from config.config import config


@st.cache_data
def _load_manufacturer_gold():
    master = pd.read_parquet(config.GOLD_DIR / "master_analytics_gold.parquet")
    manufacturer = pd.read_parquet(config.GOLD_DIR / "manufacturer_gold.parquet")
    return master, manufacturer


def _render_manufacturer_page():
    st.set_page_config(page_title="Manufacturer Insights - EV Intelligence", page_icon="🏭", layout="wide")
    st.title("Manufacturer Insights")
    master, manufacturer = _load_manufacturer_gold()
    selected = st.selectbox("Select manufacturer", sorted(master["manufacturer"].dropna().unique()))
    data = master[master["manufacturer"] == selected]

    c1, c2, c3 = st.columns(3)
    c1.metric("Sales", f"{data['sales_amount'].sum():,.0f}")
    c2.metric("Revenue", f"${data['revenue'].sum():,.0f}")
    market_share = (data["sales_amount"].sum() / max(master["sales_amount"].sum(), 1)) * 100
    c3.metric("Market Share", f"{market_share:.2f}%")

    by_state = data.groupby("state", as_index=False)["sales_amount"].sum().sort_values("sales_amount", ascending=False)
    st.bar_chart(by_state, x="state", y="sales_amount")
    st.dataframe(manufacturer.sort_values("sales_amount", ascending=False), use_container_width=True)


_render_manufacturer_page()
st.stop()

st.set_page_config(
    page_title="Manufacturer Insights - EV Intelligence",
    page_icon="🏭",
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
    manufacturer_performance = pd.read_csv('../data/processed/manufacturer_performance.csv')
    merged_data = pd.read_csv('../data/processed/merged_analytics_data.csv')
    
    ev_sales['date'] = pd.to_datetime(ev_sales['date'])
    merged_data['date'] = pd.to_datetime(merged_data['date'])
    
    return {
        'ev_sales': ev_sales,
        'manufacturer_performance': manufacturer_performance,
        'merged_data': merged_data
    }

def main():
    data = load_data()
    
    st.markdown("# 🏭 Manufacturer Intelligence Dashboard")
    st.markdown("---")
    
    # Manufacturer selection
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_manufacturer = st.selectbox(
            "Select Manufacturer for Analysis",
            sorted(data['ev_sales']['manufacturer'].unique())
        )
    
    with col2:
        analysis_type = st.selectbox("Analysis Type", ["Performance", "Competitive", "Portfolio"])
    
    with col3:
        comparison_mode = st.checkbox("Compare Manufacturers")
    
    # Manufacturer data
    manufacturer_data = data['ev_sales'][data['ev_sales']['manufacturer'] == selected_manufacturer]
    
    # KPI Cards
    total_sales = manufacturer_data['sales_amount'].sum()
    total_revenue = manufacturer_data['revenue'].sum()
    market_share = (total_sales / data['ev_sales']['sales_amount'].sum()) * 100
    avg_price = manufacturer_data['price_avg'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Sales</h3>
            <h2>{total_sales:,}</h2>
            <p>Units Sold</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Revenue</h3>
            <h2>${total_revenue:,.2f}</h2>
            <p>Market Value</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Market Share</h3>
            <h2>{market_share:.2f}%</h2>
            <p>National Share</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg Price</h3>
            <h2>${avg_price:,.0f}</h2>
            <p>Price Point</p>
        </div>
        """, unsafe_allow_html=True)
    
    if analysis_type == "Performance":
        performance_analysis(data, manufacturer_data, selected_manufacturer)
    elif analysis_type == "Competitive":
        competitive_analysis(data, manufacturer_data, selected_manufacturer, comparison_mode)
    elif analysis_type == "Portfolio":
        portfolio_analysis(data, manufacturer_data, selected_manufacturer)

def performance_analysis(data, manufacturer_data, selected_manufacturer):
    st.markdown("## 📊 Performance Analysis")
    
    # Temporal performance
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales trend
        monthly_sales = manufacturer_data.groupby(manufacturer_data['date'].dt.to_period('M')).agg({
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
            title_text=f"{selected_manufacturer} Monthly Performance"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Geographic distribution
        state_performance = manufacturer_data.groupby('state').agg({
            'sales_amount': 'sum',
            'revenue': 'sum',
            'market_share': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=state_performance['sales_amount'],
            y=state_performance['market_share'],
            mode='markers+text',
            text=state_performance['state'],
            textposition="top center",
            marker=dict(
                size=state_performance['revenue']/500000,
                color=state_performance['sales_amount'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sales Volume")
            ),
            name='States'
        ))
        
        fig.update_layout(
            title=f"{selected_manufacturer} State Performance",
            xaxis_title="Sales Volume",
            yaxis_title="Market Share",
            template="plotly_dark",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance metrics
    st.markdown("### 📈 Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Growth rate calculation
        if len(monthly_sales) >= 2:
            growth_rate = ((monthly_sales['sales_amount'].iloc[-1] - monthly_sales['sales_amount'].iloc[0]) / 
                          monthly_sales['sales_amount'].iloc[0]) * 100
            st.metric("Sales Growth", f"{growth_rate:.1f}%")
        
        # Top performing state
        top_state = state_performance.loc[state_performance['sales_amount'].idxmax()]
        st.metric("Top State", top_state['state'])
    
    with col2:
        # Average monthly sales
        avg_monthly = monthly_sales['sales_amount'].mean()
        st.metric("Avg Monthly Sales", f"{avg_monthly:.0f}")
        
        # Revenue per unit
        revenue_per_unit = total_revenue / total_sales
        st.metric("Revenue per Unit", f"${revenue_per_unit:,.0f}")
    
    with col3:
        # Market leadership
        manufacturer_rank = data['manufacturer_performance'][
            data['manufacturer_performance']['manufacturer'] == selected_manufacturer
        ]['manufacturer_rank'].iloc[0]
        st.metric("National Rank", f"#{manufacturer_rank}")
        
        # States presence
        states_count = manufacturer_data['state'].nunique()
        st.metric("States Presence", f"{states_count}")

def competitive_analysis(data, manufacturer_data, selected_manufacturer, comparison_mode):
    st.markdown("## 🥊 Competitive Analysis")
    
    if comparison_mode:
        comparison_manufacturers = st.multiselect(
            "Select Manufacturers to Compare",
            sorted(data['ev_sales']['manufacturer'].unique()),
            default=[selected_manufacturer]
        )
        
        if len(comparison_manufacturers) > 1:
            comparison_data = data['ev_sales'][data['ev_sales']['manufacturer'].isin(comparison_manufacturers)]
            
            # Comparison charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Sales comparison
                comp_sales = comparison_data.groupby(['manufacturer', comparison_data['date'].dt.to_period('M')])['sales_amount'].sum().reset_index()
                comp_sales['date'] = comp_sales['date'].dt.to_timestamp()
                
                fig = go.Figure()
                for manufacturer in comparison_manufacturers:
                    mfg_data = comp_sales[comp_sales['manufacturer'] == manufacturer]
                    fig.add_trace(go.Scatter(
                        x=mfg_data['date'],
                        y=mfg_data['sales_amount'],
                        mode='lines+markers',
                        name=manufacturer
                    ))
                
                fig.update_layout(
                    title="Sales Volume Comparison",
                    xaxis_title="Date",
                    yaxis_title="Sales Amount",
                    template="plotly_dark",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Market share comparison
                market_share_data = comparison_data.groupby('manufacturer')['sales_amount'].sum()
                
                fig = go.Figure(data=[
                    go.Pie(
                        labels=market_share_data.index,
                        values=market_share_data.values,
                        hole=0.3
                    )
                ])
                
                fig.update_layout(
                    title="Market Share Comparison",
                    template="plotly_dark",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Competitive positioning matrix
            st.markdown("### 🎯 Competitive Positioning")
            
            comp_metrics = comparison_data.groupby('manufacturer').agg({
                'sales_amount': 'sum',
                'price_avg': 'mean',
                'battery_capacity': 'mean',
                'revenue': 'sum'
            }).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=comp_metrics['price_avg'],
                y=comp_metrics['sales_amount'],
                mode='markers+text',
                text=comp_metrics['manufacturer'],
                textposition="top center",
                marker=dict(
                    size=comp_metrics['battery_capacity']/5,
                    color=comp_metrics['revenue'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Revenue")
                ),
                name='Manufacturers'
            ))
            
            fig.update_layout(
                title="Competitive Positioning Matrix",
                xaxis_title="Average Price",
                yaxis_title="Sales Volume",
                template="plotly_dark",
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Market leader analysis
    st.markdown("### 🏆 Market Leadership Analysis")
    
    # Calculate market leadership metrics
    market_leadership = data['ev_sales'].groupby('manufacturer').agg({
        'sales_amount': 'sum',
        'revenue': 'sum',
        'price_avg': 'mean',
        'battery_capacity': 'mean'
    }).reset_index()
    
    market_leadership['market_share'] = (market_leadership['sales_amount'] / market_leadership['sales_amount'].sum()) * 100
    market_leadership['price_positioning'] = pd.cut(
        market_leadership['price_avg'],
        bins=3,
        labels=['Economy', 'Mid-Range', 'Premium']
    )
    
    # Leadership table
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Market Share Leaders")
        top_manufacturers = market_leadership.nlargest(10, 'market_share')[['manufacturer', 'market_share', 'sales_amount']]
        st.dataframe(top_manufacturers, use_container_width=True)
    
    with col2:
        st.markdown("#### 💰 Revenue Leaders")
        revenue_leaders = market_leadership.nlargest(10, 'revenue')[['manufacturer', 'revenue', 'price_avg']]
        st.dataframe(revenue_leaders, use_container_width=True)

def portfolio_analysis(data, manufacturer_data, selected_manufacturer):
    st.markdown("## 🚗 Product Portfolio Analysis")
    
    # Product mix analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Vehicle category distribution
        category_sales = manufacturer_data.groupby('vehicle_category')['sales_amount'].sum()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=category_sales.index,
                values=category_sales.values,
                hole=0.3
            )
        ])
        
        fig.update_layout(
            title=f"{selected_manufacturer} Product Mix by Category",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Vehicle type distribution
        type_sales = manufacturer_data.groupby('vehicle_type')['sales_amount'].sum().sort_values(ascending=False)
        
        fig = go.Figure(data=[
            go.Bar(
                x=type_sales.values,
                y=type_sales.index,
                orientation='h',
                marker=dict(color='#4ECDC4')
            )
        ])
        
        fig.update_layout(
            title=f"{selected_manufacturer} Sales by Vehicle Type",
            xaxis_title="Sales Amount",
            yaxis_title="Vehicle Type",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Product performance metrics
    st.markdown("### 📈 Product Performance Metrics")
    
    product_metrics = manufacturer_data.groupby(['vehicle_category', 'vehicle_type']).agg({
        'sales_amount': 'sum',
        'revenue': 'sum',
        'price_avg': 'mean',
        'battery_capacity': 'mean',
        'charging_time': 'mean'
    }).reset_index()
    
    # Price vs performance analysis
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=product_metrics['price_avg'],
            y=product_metrics['battery_capacity'],
            mode='markers+text',
            text=product_metrics['vehicle_type'],
            textposition="top center",
            marker=dict(
                size=product_metrics['sales_amount']/50,
                color=product_metrics['revenue'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Revenue")
            ),
            name='Products'
        ))
        
        fig.update_layout(
            title="Price vs Battery Capacity",
            xaxis_title="Average Price",
            yaxis_title="Battery Capacity (kWh)",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Efficiency analysis
        product_metrics['price_per_kwh'] = product_metrics['price_avg'] / product_metrics['battery_capacity']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=product_metrics['vehicle_type'],
            y=product_metrics['price_per_kwh'],
            marker=dict(color='#FFD93D')
        ))
        
        fig.update_layout(
            title="Price per kWh by Vehicle Type",
            xaxis_title="Vehicle Type",
            yaxis_title="Price per kWh ($)",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Portfolio insights
    st.markdown("### 💡 Portfolio Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        best_selling = product_metrics.loc[product_metrics['sales_amount'].idxmax()]
        st.markdown(f"""
        <div class="insight-card">
            <h4>🏆 Best Selling</h4>
            <p><strong>{best_selling['vehicle_type']}</strong></p>
            <p>Sales: {best_selling['sales_amount']:,} units</p>
            <p>Revenue: ${best_selling['revenue']:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        highest_margin = product_metrics.loc[product_metrics['price_avg'].idxmax()]
        st.markdown(f"""
        <div class="insight-card">
            <h4>💎 Premium Product</h4>
            <p><strong>{highest_margin['vehicle_type']}</strong></p>
            <p>Price: ${highest_margin['price_avg']:,.0f}</p>
            <p>Battery: {highest_margin['battery_capacity']:.0f} kWh</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        best_value = product_metrics.loc[product_metrics['price_per_kwh'].idxmin()]
        st.markdown(f"""
        <div class="insight-card">
            <h4>⚡ Best Value</h4>
            <p><strong>{best_value['vehicle_type']}</strong></p>
            <p>Price/kWh: ${best_value['price_per_kwh']:.2f}</p>
            <p>Efficiency Leader</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
