
import pandas as pd
import plotly.express as px

# ALERT GENERATION
def generate_alerts(df):
    """
    Generate formatted alert report for Streamlit display.
    Returns a well-structured multi-line string.
    """

    if len(df) == 0:
        return "No data available."

    high_risk_count = df[df["risk_class"] == "High Risk"].shape[0]
    moderate_risk_count = df[df["risk_class"] == "Moderate Risk"].shape[0]

    total_cases = len(df)

    high_pct = (high_risk_count / total_cases) * 100 if total_cases else 0
    mod_pct = (moderate_risk_count / total_cases) * 100 if total_cases else 0

    # ✅ Structured lines
    report = []
    report.append("ALERT SUMMARY")
    report.append("----------------------------")
    report.append(f"Total cases        : {total_cases}")
    report.append(f"High Risk cases    : {high_risk_count} ({high_pct:.1f}%)")
    report.append(f"Moderate Risk cases: {moderate_risk_count} ({mod_pct:.1f}%)")
    report.append("")  # blank line for spacing

    # ✅ Alert decision
    if high_pct > 20:
        report.append("🔴 ALERT:")
        report.append("Too many high-risk neonates.")
        report.append("Immediate intervention needed.")

    elif mod_pct > 30:
        report.append("🟡 WARNING:")
        report.append("Moderate risk cases rising.")
        report.append("Monitor closely.")

    else:
        report.append("🟢 STATUS:")
        report.append("Risk levels acceptable.")

    # ✅ Join with proper line breaks
    return "\n".join(report)


