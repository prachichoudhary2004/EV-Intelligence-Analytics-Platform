import plotly.graph_objects as go

# Professional Fintech-inspired palette
SERIES = ["#2563eb", "#10b981", "#0ea5e9", "#f59e0b", "#8b5cf6", "#ec4899"]
BG_COLOR = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(255,255,255,0.06)"
TEXT_COLOR = "#94a3b8"

def style_plotly(fig: go.Figure, height: int = 300) -> go.Figure:
    """Apply a consistent, premium enterprise theme to Plotly charts."""
    fig.update_layout(
        height=height,
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, size=10, family="Inter, sans-serif"),
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="right",
            x=1,
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=9),
            title_font=dict(size=10, color="#64748b")
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=9),
            title_font=dict(size=10, color="#64748b")
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#161b22", font_size=11, font_family="Inter", bordercolor="rgba(255,255,255,0.1)")
    )
    return fig
