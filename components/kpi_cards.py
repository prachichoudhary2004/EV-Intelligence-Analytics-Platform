import html

import streamlit as st


def kpi_card(label, value, trend=None, trend_up=True, prefix="", suffix=""):
    trend_html = ""
    # Simple static SVG sparkline for visual effect
    sparkline_color = "#10b981" if trend_up else "#ef4444"
    sparkline = f"""<svg width="50" height="15" viewBox="0 0 50 15" fill="none" xmlns="http://www.w3.org/2000/svg" style="float:right; opacity:0.8; margin-top:2px;">
<path d="M0 12 Q 10 2, 20 8 T 50 2" stroke="{sparkline_color}" stroke-width="1.5" fill="none"/>
</svg>""" if trend is not None else ""

    if trend is not None:
        color = "#10b981" if trend_up else "#ef4444"
        arrow = "↑" if trend_up else "↓"
        trend_html = (
            f'<div class="kpi-trend" style="color:{color}">{arrow} {trend}% vs year ago</div>'
        )

    st.markdown(
        f"""<div class="metric-card">
{sparkline}
<div class="kpi-title">{html.escape(str(label))}</div>
<div class="kpi-value">{html.escape(str(prefix))}{html.escape(str(value))}{html.escape(str(suffix))}</div>
{trend_html}
</div>""",
        unsafe_allow_html=True,
    )


def live_ticker(data_items):
    """
    Status strip — avoids relying on fragile HTML-in-markdown for nested widgets.
    Renders as a single escaped line so Streamlit never shows raw Python tuples.
    """
    parts = []
    for item in data_items:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            label, val = str(item[0]), str(item[1])
            parts.append(f"{html.escape(label)}: {html.escape(val)}")
        else:
            parts.append(html.escape(str(item)))
    line = "   |   ".join(parts)
    st.markdown(
        f"<div class='ticker-container' style='white-space:normal;'>{line}</div>",
        unsafe_allow_html=True,
    )
