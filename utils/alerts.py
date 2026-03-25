import pandas as pd
import plotly.express as px

def generate_alerts(df):
    """
    Generate early warning alerts based on neonatal risk.
    """

    if len(df) == 0:
        return "No data available."

    # ✅ FIXED LABELS
    high_risk_count = df[df["risk_class"] == "High Risk"].shape[0]
    moderate_risk_count = df[df["risk_class"] == "Moderate Risk"].shape[0]

    total_cases = len(df)

    high_pct = (high_risk_count / total_cases) * 100
    mod_pct = (moderate_risk_count / total_cases) * 100

    msg = f"Total cases: {total_cases}\n"
    msg += f"High Risk: {high_risk_count} ({high_pct:.1f}%)\n"
    msg += f"Moderate Risk: {moderate_risk_count} ({mod_pct:.1f}%)\n"

    if high_pct > 20:
        msg += "🔴 ALERT: Too many high-risk neonates. Immediate intervention needed."
    elif mod_pct > 30:
        msg += "🟡 WARNING: Moderate risk cases rising. Monitor closely."
    else:
        msg += "🟢 Risk levels acceptable."

    return msg


def plot_national_risk(df, geojson_file, state_column="state", risk_column="risk_score"):
    import json

    if state_column not in df.columns:
        raise ValueError("State column missing in dataset")

    state_risk = df.groupby(state_column)[risk_column].mean().reset_index()

    with open(geojson_file, "r") as f:
        geojson = json.load(f)

    fig = px.choropleth(
        state_risk,
        geojson=geojson,
        locations=state_column,
        featureidkey="properties.STATENAME",
        color=risk_column,
        color_continuous_scale="Reds",
        range_color=(0, 1),
        labels={risk_column: "Average Risk"},
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig
