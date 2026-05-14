import streamlit as st


class DesignSystem:
    """Fintech Enterprise Tokens."""

    COLORS = {
        "primary": "#2563eb",
        "primary_muted": "#1d4ed8",
        "secondary": "#64748b",
        "accent": "#10b981",
        "background": "#050816",
        "surface": "#0b1120",
        "surface_2": "#161b22",
        "text": "#f8fafc",
        "text_secondary": "#94a3b8",
        "border": "rgba(255,255,255,0.06)",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "info": "#3b82f6",
    }

    FONTS = {
        "main": "Inter, Manrope, IBM Plex Sans, sans-serif",
        "mono": "ui-monospace, SFMono-Regular, Menlo, monospace",
    }

    SPACING = {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px"}

    BORDER_RADIUS = "6px"
    CARD_BG = "var(--surface-2)"

    @classmethod
    def apply_custom_css(cls) -> None:
        c = cls.COLORS
        st.markdown(
            f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            /* ── KILL STREAMLIT TOP WHITE BAR ── */
            header[data-testid="stHeader"] {{
                display: none !important;
                height: 0 !important;
            }}
            #MainMenu {{ display: none !important; }}
            footer {{ display: none !important; }}
            [data-testid="stToolbar"] {{ display: none !important; }}
            [data-testid="stDecoration"] {{ display: none !important; }}

            :root {{
                --primary: {c['primary']};
                --bg: {c['background']};
                --surface: {c['surface']};
                --text: {c['text']};
                --muted: {c['text_secondary']};
                --border: {c['border']};
            }}

            .stApp {{
                background-color: {c['background']};
                color: {c['text']};
                font-family: {cls.FONTS['main']};
            }}

            [data-testid="stSidebar"] {{
                background-color: {c['surface']} !important;
                border-right: 1px solid {c['border']};
                min-width: 280px !important;
                max-width: 280px !important;
            }}

            .block-container {{
                padding-top: 0.5rem;
                padding-bottom: 2rem;
                max-width: 1320px;
            }}

            .glass-card {{
                background: {cls.CARD_BG};
                border: 1px solid {c['border']};
                border-radius: {cls.BORDER_RADIUS};
                padding: {cls.SPACING['lg']};
                margin-bottom: {cls.SPACING['md']};
            }}

            div[data-testid="stMetricValue"] {{
                color: {c['text']} !important;
            }}
        </style>
        """,
            unsafe_allow_html=True,
        )


theme = DesignSystem()
