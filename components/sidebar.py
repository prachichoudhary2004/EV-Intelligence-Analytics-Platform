import streamlit as st
from datetime import datetime


NAV_ITEMS = [
    ("📊", "Executive Dashboard",  "High-level KPIs & national trends"),
    ("🗺️", "State Analytics",      "State-level drill-down"),
    ("🧭", "Market Intelligence",  "Ecosystem & segmentation"),
    ("🏭", "Manufacturer Insights","OEM benchmarks & revenue"),
    ("🔮", "Forecasting",          "Prophet demand projections"),
    ("⚙️", "Data Health & ML Ops", "Pipeline & model monitoring"),
    ("🔗", "API Gateway",          "Developer endpoint portal"),
]


def render_sidebar_dynamic(region_label: str) -> str:
    with st.sidebar:

        # ── Platform Brand Header ─────────────────────────────────
        st.markdown(
            f"""
            <div style="
                padding: 24px 20px 18px 20px;
                background: linear-gradient(135deg, rgba(37,99,235,0.12) 0%, rgba(16,185,129,0.06) 100%);
                border-bottom: 1px solid rgba(255,255,255,0.06);
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin-bottom: 6px;
                ">
                    <div style="
                        background: linear-gradient(135deg, #2563eb, #10b981);
                        border-radius: 8px;
                        width: 34px;
                        height: 34px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.1rem;
                        flex-shrink: 0;
                    ">⚡</div>
                    <div>
                        <div style="
                            font-size: 0.95rem;
                            font-weight: 700;
                            color: #f8fafc;
                            letter-spacing: -0.01em;
                            line-height: 1.2;
                        ">EV Market Intelligence</div>
                        <div style="
                            font-size: 0.72rem;
                            color: #10b981;
                            font-weight: 500;
                            letter-spacing: 0.02em;
                        ">{region_label} Analytics Platform</div>
                    </div>
                </div>
                <div style="
                    font-size: 0.68rem;
                    color: #64748b;
                    margin-top: 8px;
                    padding: 4px 8px;
                    background: rgba(255,255,255,0.03);
                    border-radius: 4px;
                    border: 1px solid rgba(255,255,255,0.05);
                ">
                    🟢 &nbsp;Live · Gold Layer · <span style="color:#94a3b8">v2.1.0</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Navigation Label ──────────────────────────────────────
        st.markdown(
            """
            <div style="
                font-size: 0.62rem;
                font-weight: 700;
                color: #475569;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                padding: 16px 20px 6px 20px;
            ">Core Analytics</div>
            """,
            unsafe_allow_html=True,
        )

        # ── Navigation Radio ──────────────────────────────────────
        labels = [item[1] for item in NAV_ITEMS]
        icons  = {item[1]: item[0] for item in NAV_ITEMS}
        descs  = {item[1]: item[2] for item in NAV_ITEMS}

        page = st.radio(
            "Navigation",
            labels,
            label_visibility="collapsed",
            format_func=lambda x: f"{icons[x]}  {x}",
        )

        # Sub-label for active page
        if page in descs:
            st.markdown(
                f"""<div style="
                    font-size: 0.68rem;
                    color: #64748b;
                    padding: 2px 20px 10px 20px;
                    margin-top: -4px;
                ">{descs[page]}</div>""",
                unsafe_allow_html=True,
            )

        # ── Divider ───────────────────────────────────────────────
        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.05);margin:12px 0;">',
            unsafe_allow_html=True,
        )

        # ── System Status Panel ───────────────────────────────────
        now_str = datetime.now().strftime("%d %b, %I:%M %p")
        st.markdown(
            f"""
            <div style="padding: 0 16px 8px 16px;">
                <div style="
                    font-size: 0.62rem;
                    font-weight: 700;
                    color: #475569;
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                    margin-bottom: 10px;
                ">System Status</div>

                <div style="display:flex;flex-direction:column;gap:7px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:0.75rem;color:#94a3b8;">API Gateway</span>
                        <span style="font-size:0.7rem;color:#10b981;font-weight:600;
                            background:rgba(16,185,129,0.1);padding:2px 8px;border-radius:10px;
                            border:1px solid rgba(16,185,129,0.2);">● Online</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:0.75rem;color:#94a3b8;">Spark Engine</span>
                        <span style="font-size:0.7rem;color:#f59e0b;font-weight:600;
                            background:rgba(245,158,11,0.1);padding:2px 8px;border-radius:10px;
                            border:1px solid rgba(245,158,11,0.2);">● Idle</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:0.75rem;color:#94a3b8;">Gold Tables</span>
                        <span style="font-size:0.7rem;color:#10b981;font-weight:600;
                            background:rgba(16,185,129,0.1);padding:2px 8px;border-radius:10px;
                            border:1px solid rgba(16,185,129,0.2);">● 4 / 4</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:0.75rem;color:#94a3b8;">Last Refresh</span>
                        <span style="font-size:0.7rem;color:#f8fafc;">{now_str}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Footer ────────────────────────────────────────────────
        st.markdown(
            f"""
            <div style="
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                padding: 12px 20px;
                border-top: 1px solid rgba(255,255,255,0.04);
                background: rgba(0,0,0,0.2);
            ">
                <div style="font-size:0.65rem;color:#475569;line-height:1.5;">
                    {region_label} EV Market Intelligence<br>
                    <span style="color:#334155;">Medallion Lakehouse · Prophet · FastAPI</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return page
