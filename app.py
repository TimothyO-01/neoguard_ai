import streamlit as st
import pandas as pd
import joblib

from utils.preprocessing import preprocess_input
from utils.prediction import predict_risk
from utils.shap_explain import shap_summary_plot, shap_single_plot
from utils.alerts import generate_alerts, plot_national_risk

# -----------------------
# Load model and features
# -----------------------
model = joblib.load("model/neoguard_model.pkl")
features = joblib.load("model/neoguard_features.pkl")

# -----------------------
# App configuration
# -----------------------
st.set_page_config(page_title="NeoGuard AI", layout="wide", page_icon="🛡️")

# -----------------------
# Header
# -----------------------
st.image("asset/logos.png", width=150)
st.title("NeoGuard AI - Neonatal Risk Early Warning System")
st.markdown("""
NeoGuard predicts neonatal complications and mortality using maternal and birth characteristics.
Supports PHC workers, hospitals, and national public health monitoring.
""")

# -----------------------
# Sidebar
# -----------------------
input_mode = st.sidebar.radio("Select Input Mode", ["Manual Entry", "Upload CSV"])

page = st.sidebar.selectbox(
    "NeoGuard Modules",
    ["Clinical Risk Assessment", "Population Dashboard", "National Risk Map", "Early Warning Alerts"]
)

# =======================
# MANUAL ENTRY
# =======================
if input_mode == "Manual Entry":

    st.subheader("Manual Neonatal Risk Prediction")

    # Better inputs (no slow +/- buttons)
    user_input = {
        "v012": st.number_input("Mother's Age (years)", min_value=10, max_value=60, value=25),
        "v149": st.selectbox("Mother's Education Level",
                             ["No education","Incomplete Primary","Complete Primary","Incomplete Secondary","Complete Secondary","Higher"]),
        "v140": st.selectbox("Residence", ["Urban", "Rural"]),
        "v190": st.selectbox("Wealth Index", ["Poorest","Poorer","Middle","Richer","Richest"]),
        "b4": st.selectbox("Child Sex", ["Male","Female"]),
        "bord": st.number_input("Birth Order", min_value=1, max_value=15, value=1),
        "b11": st.number_input("Birth Interval (months)", min_value=0, max_value=60, value=24),
        "m15": st.selectbox("Place of Delivery", ["Home","PHC","Hospital/Clinic"]),
        "m14": st.number_input("Number of ANC Visits", min_value=0, max_value=20, value=4),
        "m1": st.selectbox("Tetanus Protection", ["Yes","No"]),
        "b0": st.selectbox("Multiple Birth", ["No","Yes"]),
        "m19": st.number_input("Birth Weight (grams)", min_value=300, max_value=6000, value=3000)
    }

    if st.button("Predict Risk"):

        try:
            input_df = pd.DataFrame([user_input])

            # Preprocess
            input_df = preprocess_input(input_df)

            # Ensure feature alignment
            for col in features:
                if col not in input_df.columns:
                    input_df[col] = 0

            input_df = input_df[features]
            st.subheader("Readable Input")
            st.write(user_input)
            st.subheader("Processed Input (Model Format)")
            st.write(input_df)

            # DEBUG 
            
            st.write("Prediction Probability:", model.predict_proba(input_df))

            # Prediction
            risk_class, risk_score = predict_risk(model, input_df)

            st.metric("Predicted Risk", f"{risk_class} ({risk_score:.2f})")

            st.subheader("Top Contributing Factors")
            shap_single_plot(model, input_df, features)

        except Exception as e:
            st.error(f"Error during prediction: {e}")



# =======================
# CSV UPLOAD
# =======================
elif input_mode == "Upload CSV":

    uploaded_file = st.file_uploader("Upload dataset (CSV)", type=["csv"])

    if uploaded_file:

        df = pd.read_csv(uploaded_file)

        df = preprocess_input(df)

        # Ensure features
        for col in features:
            if col not in df.columns:
                df[col] = 0

        df = df[features]

        # Compute predictions
        probs = model.predict_proba(df)[:, 1]
        df["risk_score"] = probs
        df["risk_class"] = df["risk_score"].apply(
            lambda x: "High Risk" if x >= 0.5 else "Low/Moderate Risk"
        )

        # -----------------------
        # MODULES
        # -----------------------

        if page == "Clinical Risk Assessment":

            st.subheader("Individual Neonatal Risk Prediction")

            st.dataframe(df.head())

            idx = st.number_input("Select row", 0, len(df)-1, 0)

            case = df.iloc[[idx]]

            risk_class, risk_score = predict_risk(model, case)

            st.metric("Predicted Risk", f"{risk_class} ({risk_score:.2f})")

            shap_single_plot(model, case, features)

        elif page == "Population Dashboard":

            st.subheader("Population Risk Distribution")

            st.bar_chart(df["risk_class"].value_counts())

            st.subheader("Key Risk Drivers")
            shap_summary_plot(model, df)

        elif page == "National Risk Map":

            st.subheader("National Neonatal Risk Map")

            fig = plot_national_risk(df, geojson_file="nigeria_states.geojson")
            st.plotly_chart(fig, use_container_width=True)

        elif page == "Early Warning Alerts":

            st.subheader("Early Warning Alerts")

            alerts = generate_alerts(df)
            st.warning(alerts)

    else:
        st.info("Upload a CSV file to activate dashboard features.")
