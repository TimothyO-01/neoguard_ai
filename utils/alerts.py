

import pandas as pd
import plotly.express as px

def generate_alerts(df):
    """
    Generate textual early warning alerts based on neonatal risk.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing 'risk_class' and 'risk_score'
    
    Returns:
        str: Alert message
    """
    # Count high-risk cases
    high_risk_count = df[df["risk_class"] == "High"].shape[0]
    medium_risk_count = df[df["risk_class"] == "Medium"].shape[0]
    
    total_cases = len(df)
    
    if total_cases == 0:
        return "No data available to generate alerts."
    
    high_risk_percent = (high_risk_count / total_cases) * 100
    medium_risk_percent = (medium_risk_count / total_cases) * 100
    
    alert_msg = f"Total cases: {total_cases}\n"
    alert_msg += f"High-risk neonates: {high_risk_count} ({high_risk_percent:.1f}%)\n"
    alert_msg += f"Medium-risk neonates: {medium_risk_count} ({medium_risk_percent:.1f}%)\n"
    
    if high_risk_percent > 20:
        alert_msg += "⚠️ Alert: High proportion of neonates at high risk. Immediate clinical attention required.\n"
    elif medium_risk_percent > 30:
        alert_msg += "⚠️ Caution: Moderate number of neonates at medium risk. Monitor closely.\n"
    else:
        alert_msg += "✅ Neonatal risk levels within acceptable range.\n"
    
    return alert_msg


def plot_national_risk(df, geojson_file, state_column="state", risk_column="risk_score"):
    """
    Plot national neonatal risk map using Plotly choropleth.
    
    Parameters:
        df (pd.DataFrame): DataFrame with state-level risk info
        geojson_file (str): Path to geojson file for states
        state_column (str): Column name for state identifiers in df
        risk_column (str): Column name for numeric risk score
    
    Returns:
        plotly.graph_objs._figure.Figure: Choropleth figure
    """
    # Aggregate by state
    state_risk = df.groupby(state_column)[risk_column].mean().reset_index()
    
    # Load geojson
    import json
    with open(geojson_file, "r") as f:
        geojson = json.load(f)
    
    fig = px.choropleth(
        state_risk,
        geojson=geojson,
        locations=state_column,
        featureidkey="properties.STATENAME",  # adjust to match your geojson
        color=risk_column,
        color_continuous_scale="Reds",
        range_color=(0, 1),
        labels={risk_column: "Average Risk Score"},
        hover_data={risk_column: ":.2f"}
    )
    
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar=dict(title="Risk Score")
    )
    
    return fig
