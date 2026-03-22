import streamlit as st
import pandas as pd
import joblib
from utils.preprocessing import preprocess_input
from utils.prediction import predict_risk
from utils.shap_explain import shap_summary_plot, shap_single_plot
from utils.alerts import generate_alerts, plot_national_risk

# Load model and features
model = joblib.load("model/neoguard_model.pkl")
features = joblib.load("model/neoguard_features.pkl")

# Friendly mapping for PHC workers
friendly_labels = {
    "v012": "Mother's Age (years)",
    "v149": "Mother's Education Level",
    "v140": "Residence (Urban/Rural)",
    "v190": "Wealth Index",
    "b4": "Child Sex",
    "bord": "Birth Order",
    "b11": "Birth Interval (months)",
    "m15": "Place of Delivery",
    "m14": "Number of ANC Visits",
    "m1": "Tetanus Protection",
    "b0": "Multiple Birth",
    "m19": "Birth Weight (grams)"
}

# App configuration
st.set_page_config(page_title="NeoGuard AI", layout="wide", page_icon="🛡️")

# Logo and header
st.image("asset/logos.png", width=150)
st.title("NeoGuard AI - Neonatal Risk Early Warning System")
st.markdown("""
NeoGuard predicts neonatal complications and mortality using maternal and birth characteristics.
Supports PHC workers, hospitals, and national public health monitoring.
""")

# Input mode
input_mode = st.sidebar.radio("Select Input Mode", ["Manual Entry", "Upload CSV"])

# Sidebar menu
page = st.sidebar.selectbox(
    "NeoGuard Modules",
    ["Clinical Risk Assessment", "Population Dashboard", "National Risk Map", "Early Warning Alerts"]
)

# ---------- Manual Entry Mode ----------
if input_mode == "Manual Entry":
    st.subheader("Manual Neonatal Risk Prediction")
    user_input = {}

    # Collect manual input (friendly UI)
    user_input["v012"] = st.text_input("Mother's Age (years)")
    user_input["v149"] = st.selectbox("Mother's Education Level", ["No education","Incomplete Primary","Complete Primary","Incomplete Secondary","Complete Secondary","Higher"])
    user_input["v140"] = st.selectbox("Residence", ["Urban", "Rural"])
    user_input["v190"] = st.selectbox("Wealth Index", ["Poorest","Poorer","Middle","Richer","Richest"])
    user_input["b4"] = st.selectbox("Child Sex", ["Male","Female"])
    user_input["bord"] = st.text_input("Birth Order")
    user_input["b11"] = st.text_input("Birth Interval (months)")
    user_input["m15"] = st.selectbox("Place of Delivery", ["Home","PHC","Hospital/Clinic"])
    user_input["m14"] = st.text_input("Number of ANC Visits")
    user_input["m1"] = st.selectbox("Tetanus Protection", ["Yes","No"])
    user_input["b0"] = st.selectbox("Multiple Birth", ["No","Yes"])
    user_input["m19"] = st.text_input("Birth Weight (grams)")

    if st.button("Predict Risk"):
        try:
            input_df = pd.DataFrame([user_input])
            input_df = preprocess_input(input_df)  # encode categorical, fill missing
            # Ensure all model features exist
            for col in features:
                if col not in input_df.columns:
                    input_df[col] = 0
            input_df = input_df[features]  # order columns as model expects

            risk_class, risk_score = predict_risk(model, input_df)
            st.metric("Predicted Risk", f"{risk_class} ({risk_score:.2f})")
            st.subheader("Top Contributing Factors (SHAP)")
            shap_single_plot(model, input_df, features)
        except Exception as e:
            st.error(f"Error during prediction: {e}")

# ---------- CSV Upload Mode ----------
elif input_mode == "Upload CSV":
    uploaded_file = st.file_uploader("Upload dataset (private or national)", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df = preprocess_input(df)
        # Ensure all features exist
        for col in features:
            if col not in df.columns:
                df[col] = 0
        df = df[features]
        
        # Calculate risk
        df["risk_class"] = df.apply(lambda row: predict_risk(model, pd.DataFrame([row]))[0], axis=1)
        df["risk_score"] = df.apply(lambda row: predict_risk(model, pd.DataFrame([row]))[1], axis=1)
        
        # Clinical Risk Assessment
        if page == "Clinical Risk Assessment":
            st.subheader("Individual Neonatal Risk Prediction")
            st.dataframe(df.head(5))
            selected_index = st.number_input("Enter row number to predict", min_value=0, max_value=len(df)-1, value=0)
            input_case = df.iloc[[selected_index]]
            risk_class, risk_score = predict_risk(model, input_case)
            st.metric("Predicted Risk", f"{risk_class} ({risk_score:.2f})")
            st.subheader("Top Contributing Factors (SHAP)")
            shap_single_plot(model, input_case, features)

        # Population Dashboard
        elif page == "Population Dashboard":
            st.subheader("Population Neonatal Risk Distribution")
            st.bar_chart(df["risk_class"].value_counts())
            st.subheader("Top Population Risk Factors")
            shap_summary_plot(model, df[features])

        # National Risk Map
        elif page == "National Risk Map":
            st.subheader("National Neonatal Risk by State")
            fig = plot_national_risk(df, geojson_file="nigeria_states.geojson")
            st.plotly_chart(fig, use_container_width=True)

        # Early Warning Alerts
        elif page == "Early Warning Alerts":
            st.subheader("Early Warning Alerts")
            st.warning(generate_alerts(df))
    else:
        st.info("Please upload a CSV to enable dashboards, national map, and alerts.")
