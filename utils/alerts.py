
import pandas as pd
import plotly.express as px


# ALERT GENERATION
def generate_alerts(df):
    """
    Generate early warning alerts based on neonatal risk.
    Returns formatted string with line breaks.
    """

    if len(df) == 0:
        return "No data available."

    high_risk_count = df[df["risk_class"] == "High Risk"].shape[0]
    moderate_risk_count = df[df["risk_class"] == "Moderate Risk"].shape[0]

    total_cases = len(df)

    high_pct = (high_risk_count / total_cases) * 100 if total_cases else 0
    mod_pct = (moderate_risk_count / total_cases) * 100 if total_cases else 0

    lines = [
        f"Total cases: {total_cases}",
        f"High Risk: {high_risk_count} ({high_pct:.1f}%)",
        f"Moderate Risk: {moderate_risk_count} ({mod_pct:.1f}%)"
    ]

    if high_pct > 20:
        lines.append("🔴 ALERT: Too many high-risk neonates. Immediate intervention needed.")
    elif mod_pct > 30:
        lines.append("🟡 WARNING: Moderate risk cases rising. Monitor closely.")
    else:
        lines.append("🟢 Risk levels acceptable.")
        
    return "\n".join(lines)


# -----------------------
# STREAMLIT DISPLAY FIX
# -----------------------
def display_alerts(msg):
    """
    Display alerts properly in Streamlit (fixes jam-packed issue)
    """

    import streamlit as st

    st.markdown(
        f"""
        <div style="
            background-color: #2d3a1f;
            padding: 15px;
            border-radius: 10px;
            color: white;
            font-size: 16px;
            line-height: 1.6;
        ">
            {msg.replace("\n", "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )



