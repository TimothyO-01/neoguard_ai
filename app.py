
import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import shap
import plotly.express as px

# Import utility functions
from utils.preprocessing import preprocess_input
from utils.prediction import predict_risk
from utils.shap_explain import shap_summary_plot, shap_single_plot
from utils.alerts import generate_alerts, plot_national_risk

# -----------------------
# Load model and features
# -----------------------
model = joblib.load("model/neoguard_model.pkl")
features = joblib.load("model/features.pkl")

# -----------------------
# App Configuration
# -----------------------
st.set_page_config(
    page_title="NeoGuard AI",
    layout="wide",
    page_icon="🛡️"
)

# -----------------------
# Welcome / Dashboard Mockup
# -----------------------

st.image(
    "assets/logos/neoguard_logo.png",
    width=150
)

st.title("NeoGuard AI - Neonatal Risk Early Warning System")
st.markdown(
"""
NeoGuard predicts neonatal complications and mortality using maternal and birth characteristics.
Supports PHC workers, hospitals, and national public health monitoring.
"""
)

# -----------------------
# Sidebar Navigation
# -----------------------
page = st.sidebar.selectbox(
    "NeoGuard Modules",
    [
        "Clinical Risk Assessment",
        "Population Dashboard",
        "National Risk Map",
        "Early Warning Alerts"
    ]
)

# -----------------------
# File Upload
# -----------------------
uploaded_file = st.file_uploader(
    "Upload dataset (private or national)",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df = preprocess_input(df)
    
    # Calculate risk
    df = df.copy()
    df["risk_class"] = df.apply(lambda row: predict_risk(model, pd.DataFrame([row]))[0], axis=1)
    df["risk_score"] = df.apply(lambda row: predict_risk(model, pd.DataFrame([row]))[1], axis=1)
    
    # -----------------------
    # Clinical Risk Assessment
    # -----------------------
    if page == "Clinical Risk Assessment":
        st.subheader("Individual Neonatal Risk Prediction")
        st.dataframe(df.head(5))
        
        selected_index = st.number_input(
            "Enter row number to predict", min_value=0, max_value=len(df)-1, value=0
        )
        input_case = df.iloc[[selected_index]]
        risk_class, risk_score = predict_risk(model, input_case)
        st.metric("Predicted Risk", f"{risk_class} ({risk_score:.2f})")
        
        st.subheader("Top Contributing Factors (SHAP)")
        shap_single_plot(model, input_case, features)

    # -----------------------
    # Population Dashboard
    # -----------------------
    elif page == "Population Dashboard":
        st.subheader("Population Neonatal Risk Distribution")
        risk_counts = df["risk_class"].value_counts()
        st.bar_chart(risk_counts)
        
        st.subheader("Top Population Risk Factors")
        shap_summary_plot(model, df[features])

    # -----------------------
    # National Risk Map
    # -----------------------
    elif page == "National Risk Map":
        st.subheader("National Neonatal Risk by State")
        fig = plot_national_risk(df, geojson_file="nigeria_states.geojson")
        st.plotly_chart(fig, use_container_width=True)
        
    # -----------------------
    # Early Warning Alerts
    # -----------------------
    elif page == "Early Warning Alerts":
        st.subheader("Early Warning Alerts")
        alert_msg = generate_alerts(df)
        st.warning(alert_msg)

else:
    st.info(
        "Please upload a CSV dataset to enable predictions, population dashboards, national map, and alerts."
)
