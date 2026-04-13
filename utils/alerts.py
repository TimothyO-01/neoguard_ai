
import pandas as pd
import plotly.express as px



# ALERT GENERATION

def generate_alerts(df):
    if len(df) == 0:
        return {
            "summary": ["No data available."],
            "status": "info"
        }

    high_risk_count = df[df["risk_class"] == "High Risk"].shape[0]
    moderate_risk_count = df[df["risk_class"] == "Moderate Risk"].shape[0]

    total_cases = len(df)

    high_pct = (high_risk_count / total_cases) * 100 if total_cases else 0
    mod_pct = (moderate_risk_count / total_cases) * 100 if total_cases else 0

    summary = [
        f"Total cases: {total_cases}",
        f"High Risk: {high_risk_count} ({high_pct:.1f}%)",
        f"Moderate Risk: {moderate_risk_count} ({mod_pct:.1f}%)"
    ]

    if high_pct > 20:
        return {
            "summary": summary,
            "status": "error",
            "message": "🔴 Too many high-risk neonates. Immediate intervention needed."
        }

    elif mod_pct > 30:
        return {
            "summary": summary,
            "status": "warning",
            "message": "🟡 Moderate risk cases rising. Monitor closely."
        }

    else:
        return {
            "summary": summary,
            "status": "success",
            "message": "🟢 Risk levels acceptable."
        }

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
        lines.append("🟢 Risk levels acceptable." )
        
    return "\n".join(lines)




