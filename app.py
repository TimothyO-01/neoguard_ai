import streamlit as st
import pandas as pd
import joblib
import shap
from utils.preprocessing import preprocess_input
from utils.prediction import predict_risk
from utils.shap_explain import shap_summary_plot, shap_single_plot

# Load model and features
model = joblib.load("model/neoguard_model.pkl")
features = joblib.load("model/features.pkl")

st.set_page_config(page_title="NeoGuard - Neonatal Early Warning System", layout="wide")

st.title("NeoGuard AI - Neonatal Risk Early Warning System")
st.markdown("""
NeoGuard predicts neonatal complications and mortality using maternal and birth characteristics.
""")

# Sidebar input
st.sidebar.header("Patient / Birth Information")
user_input = {}
for f in features:
    user_input[f] = st.sidebar.text_input(f)

# Convert input to DataFrame
input_df = pd.DataFrame([user_input])
input_df = preprocess_input(input_df)  # Handle missing values, encoding

# Prediction
if st.button("Predict Risk"):
    risk, risk_score = predict_risk(model, input_df)
    st.subheader(f"Predicted Neonatal Risk: {risk} (Score: {risk_score:.2f})")

    # SHAP explainability
    st.subheader("Top Contributing Risk Factors")
    shap_single_plot(model, input_df, features)
    
# SHAP global summary
if st.checkbox("Show Global Risk Factors"):
    shap_summary_plot(model, features)
