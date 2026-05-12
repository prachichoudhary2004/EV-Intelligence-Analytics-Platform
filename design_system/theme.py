import streamlit as st

class DesignSystem:
    """
    Standardized design tokens and theme settings for a premium UI.
    """
    # Color Palette
    COLORS = {
        "primary": "#00FF41",      # Matrix Green
        "secondary": "#FF6B6B",    # Soft Coral
        "accent": "#4ECDC4",       # Turquoise
        "background": "#0E1117",   # Deep Space
        "surface": "#1E2139",      # Indigo Navy
        "text": "#FFFFFF",         # Pure White
        "text_secondary": "#A0A0A0", # Muted Gray
        "success": "#28A745",
        "warning": "#FFC107",
        "danger": "#DC3545",
        "info": "#17A2B8"
    }
    
    # Typography
    FONTS = {
        "main": "Inter, sans-serif",
        "mono": "Space Mono, monospace"
    }
    
    # Spacing & Borders
    SPACING = {
        "xs": "4px",
        "sm": "8px",
        "md": "16px",
        "lg": "24px",
        "xl": "32px"
    }
    
    BORDER_RADIUS = "12px"
    GLASS_EFFECT = "rgba(255, 255, 255, 0.05)"
    
    @classmethod
    def apply_custom_css(cls):
        """Inject professional CSS into Streamlit."""
        st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Space+Mono&display=swap');
            
            :root {{
                --primary: {cls.COLORS['primary']};
                --background: {cls.COLORS['background']};
                --surface: {cls.COLORS['surface']};
            }}
            
            .stApp {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['text']};
                font-family: {cls.FONTS['main']};
            }}
            
            /* Glassmorphism Card */
            .glass-card {{
                background: {cls.GLASS_EFFECT};
                backdrop-filter: blur(10px);
                border-radius: {cls.BORDER_RADIUS};
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: {cls.SPACING['lg']};
                margin-bottom: {cls.SPACING['md']};
                transition: transform 0.3s ease, border-color 0.3s ease;
            }}
            
            .glass-card:hover {{
                transform: translateY(-5px);
                border-color: {cls.COLORS['primary']};
            }}
            
            /* KPI Metrics */
            .kpi-label {{
                font-size: 0.9rem;
                color: {cls.COLORS['text_secondary']};
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .kpi-value {{
                font-size: 2rem;
                font-weight: 700;
                color: {cls.COLORS['primary']};
                margin: {cls.SPACING['xs']} 0;
            }}
            
            .kpi-trend {{
                font-size: 0.85rem;
                font-weight: 600;
            }}
            
            .trend-up {{ color: {cls.COLORS['success']}; }}
            .trend-down {{ color: {cls.COLORS['danger']}; }}
            
            /* Custom Scrollbar */
            ::-webkit-scrollbar {{
                width: 8px;
            }}
            ::-webkit-scrollbar-track {{
                background: {cls.COLORS['background']};
            }}
            ::-webkit-scrollbar-thumb {{
                background: {cls.COLORS['surface']};
                border-radius: 10px;
            }}
            ::-webkit-scrollbar-thumb:hover {{
                background: {cls.COLORS['primary']};
            }}
        </style>
        """, unsafe_allow_html=True)

theme = DesignSystem()
