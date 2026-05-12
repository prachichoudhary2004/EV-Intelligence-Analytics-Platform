import streamlit as st

def render_sidebar():
    """
    Renders a professional enterprise sidebar with branding and navigation.
    """
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #00FF41; margin-bottom: 0;">⚡ EV CORE</h1>
            <p style="color: #A0A0A0; font-size: 0.8rem; letter-spacing: 2px;">ENTERPRISE INTELLIGENCE</p>
        </div>
        <hr style="border: 0.5px solid rgba(255,255,255,0.1);">
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### 🧭 NAVIGATION")
        page = st.radio("", [
            "📊 Executive Summary",
            "🌐 Market Intelligence",
            "📈 ML Sales Forecasting",
            "🧪 Data Health & ML Ops",
            "🛂 API & Integration"
        ])
        
        st.markdown("---")
        
        # System Status
        st.markdown("### ⚙️ SYSTEM STATUS")
        st.success("API: Operational")
        st.info("Engine: Spark 3.4.1")
        st.warning("Storage: Delta Lake Simulation")
        
        st.markdown("---")
        st.caption("v1.2.0 | Enterprise Edition")
        
    return page
