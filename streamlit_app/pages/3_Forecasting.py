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
from models.forecaster import forecaster


@st.cache_data
def _load_master():
    df = pd.read_parquet(config.GOLD_DIR / "master_analytics_gold.parquet")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def _render_forecasting_page():
    st.set_page_config(page_title="Forecasting - EV Intelligence", page_icon="📈", layout="wide")
    st.title("Forecasting")
    master = _load_master()
    periods = st.slider("Forecast periods (months)", min_value=3, max_value=24, value=12)
    forecast_df = forecaster.forecast_prophet(master, periods=periods)
    st.line_chart(forecast_df, x="ds", y=["yhat", "yhat_lower", "yhat_upper"])
    st.dataframe(forecast_df.tail(periods), use_container_width=True)


_render_forecasting_page()
st.stop()

st.set_page_config(
    page_title="Forecasting - EV Intelligence",
    page_icon="📈",
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
    try:
        monthly_sales = pd.read_csv('../data/processed/monthly_sales.csv')
        ev_sales = pd.read_csv('../data/processed/ev_sales_clean.csv')
        merged_data = pd.read_csv('../data/processed/merged_analytics_data.csv')
        
        monthly_sales['month_year'] = pd.to_datetime(monthly_sales['month_year'])
        ev_sales['date'] = pd.to_datetime(ev_sales['date'])
        merged_data['date'] = pd.to_datetime(merged_data['date'])
        
        return {
            'monthly_sales': monthly_sales,
            'ev_sales': ev_sales,
            'merged_data': merged_data
        }
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def generate_forecast(historical_data, periods=12, confidence_level=90):
    """Generate forecast using simple linear trend with seasonality"""
    # Extract trend
    x = np.arange(len(historical_data))
    y = historical_data.values
    
    # Linear trend
    trend_coef = np.polyfit(x, y, 1)
    trend_values = np.polyval(trend_coef, x)
    
    # Seasonal component (simplified)
    if len(historical_data) >= 12:
        seasonal_component = y - trend_values
        monthly_seasonal = np.array([
            np.mean(seasonal_component[i::12]) for i in range(12)
        ])
    else:
        monthly_seasonal = np.zeros(12)
    
    # Generate future dates
    last_date = historical_data.index[-1]
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=periods,
        freq='M'
    )
    
    # Generate forecast
    future_x = np.arange(len(historical_data), len(historical_data) + periods)
    future_trend = np.polyval(trend_coef, future_x)
    
    # Add seasonal component
    future_seasonal = np.array([
        monthly_seasonal[i % 12] for i in range(periods)
    ])
    
    forecast_values = future_trend + future_seasonal
    
    # Add confidence intervals
    confidence_multiplier = confidence_level / 100
    std_error = np.std(y - trend_values)
    margin_of_error = std_error * confidence_multiplier
    
    upper_bound = forecast_values + margin_of_error
    lower_bound = np.maximum(0, forecast_values - margin_of_error)  # Ensure non-negative
    
    return {
        'dates': future_dates,
        'forecast': forecast_values,
        'upper_bound': upper_bound,
        'lower_bound': lower_bound
    }

def main():
    data = load_data()
    
    if not data:
        st.error("Unable to load data. Please ensure data files are available.")
        return
    
    st.markdown("# 📈 EV Sales Forecasting")
    st.markdown("---")
    
    # Forecast configuration
    st.markdown("### ⚙️ Forecast Configuration")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        forecast_period = st.selectbox("Forecast Period (Months)", [3, 6, 12, 18, 24], index=2)
    
    with col2:
        forecast_level = st.selectbox("Forecast Level", ["National", "State", "Manufacturer"])
    
    with col3:
        confidence_level = st.selectbox("Confidence Level", [80, 85, 90, 95], index=2)
    
    with col4:
        model_type = st.selectbox("Forecast Model", ["Linear Trend", "Moving Average", "Exponential Smoothing"])
    
    # Level-specific filters
    if forecast_level == "State":
        selected_state = st.selectbox(
            "Select State",
            sorted(data['ev_sales']['state'].unique())
        )
    elif forecast_level == "Manufacturer":
        selected_manufacturer = st.selectbox(
            "Select Manufacturer",
            sorted(data['ev_sales']['manufacturer'].unique())
        )
    
    # Generate forecast button
    if st.button("🚀 Generate Forecast", type="primary"):
        with st.spinner("Generating forecast..."):
            # Prepare data based on forecast level
            if forecast_level == "National":
                historical_data = data['monthly_sales'].groupby('month_year')['sales_amount'].sum()
                title = "National EV Sales Forecast"
            elif forecast_level == "State":
                state_data = data['ev_sales'][data['ev_sales']['state'] == selected_state]
                historical_data = state_data.groupby(state_data['date'].dt.to_period('M'))['sales_amount'].sum()
                title = f"{selected_state} EV Sales Forecast"
            else:  # Manufacturer
                mfg_data = data['ev_sales'][data['ev_sales']['manufacturer'] == selected_manufacturer]
                historical_data = mfg_data.groupby(mfg_data['date'].dt.to_period('M'))['sales_amount'].sum()
                title = f"{selected_manufacturer} EV Sales Forecast"
            
            # Generate forecast
            forecast_result = generate_forecast(historical_data, forecast_period, confidence_level)
            
            # Create forecast visualization
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=historical_data.index,
                y=historical_data.values,
                mode='lines+markers',
                name='Historical',
                line=dict(color='white', width=3),
                marker=dict(size=6)
            ))
            
            # Forecast
            fig.add_trace(go.Scatter(
                x=forecast_result['dates'],
                y=forecast_result['forecast'],
                mode='lines+markers',
                name='Forecast',
                line=dict(color='#00FF41', width=3, dash='dash'),
                marker=dict(size=6)
            ))
            
            # Confidence intervals
            fig.add_trace(go.Scatter(
                x=forecast_result['dates'].tolist() + forecast_result['dates'].tolist()[::-1],
                y=forecast_result['upper_bound'].tolist() + forecast_result['lower_bound'].tolist()[::-1],
                fill='toself',
                fillcolor=f'rgba(0, 255, 65, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=True,
                name=f'{confidence_level}% Confidence Band'
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Sales Amount",
                template="plotly_dark",
                height=600,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_forecast = np.sum(forecast_result['forecast'])
            avg_monthly = total_forecast / forecast_period
            current_monthly = historical_data.iloc[-3:].mean()
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Forecast</h3>
                    <h2>{total_forecast:,.0f}</h2>
                    <p>{forecast_period} Month Total</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Avg Monthly</h3>
                    <h2>{avg_monthly:,.0f}</h2>
                    <p>Per Month</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                growth_rate = ((forecast_result['forecast'][-1] - forecast_result['forecast'][0]) / 
                              forecast_result['forecast'][0]) * 100
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Growth Rate</h3>
                    <h2>{growth_rate:.1f}%</h2>
                    <p>Forecast Period</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                forecast_change = ((avg_monthly - current_monthly) / current_monthly) * 100
                st.markdown(f"""
                <div class="metric-card">
                    <h3>vs Current</h3>
                    <h2>{forecast_change:+.1f}%</h2>
                    <p>vs Recent Avg</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Model comparison
    st.markdown("### 🤖 Model Performance Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Model Accuracy Metrics")
        
        # Simulate model performance data
        model_performance = pd.DataFrame({
            'Model': ['Linear Trend', 'Moving Average', 'Exponential Smoothing', 'Random Forest', 'Neural Network'],
            'MAE': [450, 520, 380, 320, 290],
            'RMSE': [680, 750, 590, 510, 470],
            'MAPE': [12.5, 14.2, 10.8, 9.3, 8.6],
            'R²': [0.82, 0.78, 0.85, 0.89, 0.91]
        })
        
        st.dataframe(model_performance, use_container_width=True)
    
    with col2:
        st.markdown("#### 🎯 Best Model Selection")
        
        best_model = model_performance.loc[model_performance['R²'].idxmax()]
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>🏆 Recommended Model</h4>
            <p><strong>{best_model['Model']}</strong></p>
            <p>R² Score: {best_model['R²']:.3f}</p>
            <p>MAPE: {best_model['MAPE']:.1f}%</p>
            <p>This model provides the best balance of accuracy and interpretability for EV sales forecasting.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Forecast scenarios
    st.markdown("### 🎭 Scenario Analysis")
    
    scenario_col1, scenario_col2, scenario_col3 = st.columns(3)
    
    with scenario_col1:
        st.markdown("#### 📈 Optimistic Scenario")
        optimistic_growth = 1.25
        optimistic_forecast = total_forecast * optimistic_growth if 'total_forecast' in locals() else 0
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>High Growth</h4>
            <p><strong>+25%</strong> vs baseline</p>
            <p>Total: {optimistic_forecast:,.0f} units</p>
            <p>Drivers: Strong policy support, rapid infrastructure expansion</p>
        </div>
        """, unsafe_allow_html=True)
    
    with scenario_col2:
        st.markdown("#### 📊 Baseline Scenario")
        baseline_growth = 1.00
        baseline_forecast = total_forecast * baseline_growth if 'total_forecast' in locals() else 0
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>Expected Growth</h4>
            <p><strong>0%</strong> vs baseline</p>
            <p>Total: {baseline_forecast:,.0f} units</p>
            <p>Drivers: Current trends continue, moderate policy environment</p>
        </div>
        """, unsafe_allow_html=True)
    
    with scenario_col3:
        st.markdown("#### 📉 Conservative Scenario")
        conservative_growth = 0.75
        conservative_forecast = total_forecast * conservative_growth if 'total_forecast' in locals() else 0
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>Low Growth</h4>
            <p><strong>-25%</strong> vs baseline</p>
            <p>Total: {conservative_forecast:,.0f} units</p>
            <p>Drivers: Supply constraints, reduced incentives, economic slowdown</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Forecast insights
    st.markdown("### 💡 Forecast Insights & Recommendations")
    
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        st.markdown("""
        <div class="insight-card">
            <h4>🔍 Key Forecast Drivers</h4>
            <ul>
                <li><strong>Seasonal Patterns:</strong> Q4 typically shows 15-20% increase</li>
                <li><strong>Policy Impact:</strong> New incentives expected in H2</li>
                <li><strong>Infrastructure:</strong> Charging network expanding at 8% quarterly</li>
                <li><strong>Technology:</strong> Battery costs declining 10% annually</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with insight_col2:
        st.markdown("""
        <div class="insight-card">
            <h4>🎯 Strategic Recommendations</h4>
            <ul>
                <li><strong>Production Planning:</strong> Scale up for Q4 demand surge</li>
                <li><strong>Inventory Management:</strong> Build buffer for supply chain risks</li>
                <li><strong>Marketing Focus:</strong> Target emerging markets with high growth</li>
                <li><strong>Investment Priorities:</strong> Expand charging infrastructure</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Historical accuracy
    st.markdown("### 📚 Historical Forecast Accuracy")
    
    # Simulate historical accuracy data
    accuracy_data = pd.DataFrame({
        'Period': ['Jan-Mar', 'Apr-Jun', 'Jul-Sep', 'Oct-Dec'],
        'Forecast': [8500, 9200, 10100, 11800],
        'Actual': [8200, 9500, 9800, 12500],
        'Accuracy': [96.3, 96.8, 97.1, 94.4]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=accuracy_data['Period'],
        y=accuracy_data['Forecast'],
        name='Forecast',
        marker_color='#00FF41'
    ))
    fig.add_trace(go.Bar(
        x=accuracy_data['Period'],
        y=accuracy_data['Actual'],
        name='Actual',
        marker_color='#FF6B6B'
    ))
    
    fig.update_layout(
        title="Forecast vs Actual Sales",
        xaxis_title="Period",
        yaxis_title="Sales Amount",
        template="plotly_dark",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Accuracy metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_accuracy = accuracy_data['Accuracy'].mean()
        st.metric("Average Accuracy", f"{avg_accuracy:.1f}%")
    
    with col2:
        max_accuracy = accuracy_data['Accuracy'].max()
        st.metric("Best Period", f"{max_accuracy:.1f}%")
    
    with col3:
        min_accuracy = accuracy_data['Accuracy'].min()
        st.metric("Lowest Period", f"{min_accuracy:.1f}%")
    
    with col4:
        forecast_bias = (accuracy_data['Forecast'].sum() - accuracy_data['Actual'].sum()) / accuracy_data['Actual'].sum() * 100
        st.metric("Forecast Bias", f"{forecast_bias:+.1f}%")

if __name__ == "__main__":
    main()
