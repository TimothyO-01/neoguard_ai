import streamlit as st
import pandas as pd
import joblib

from utils.preprocessing import preprocess_input
from utils.shap_explain import shap_summary_plot, shap_single_plot
from utils.alerts import generate_alerts, plot_national_risk

# -----------------------
# Load model
# -----------------------
model = joblib.load("model/neoguard_model.pkl")
features = joblib.load("model/neoguard_features.pkl")

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="NeoGuard AI", layout="wide", page_icon="🛡️")

# -----------------------
# Header
# -----------------------
st.image("asset/logos.png", width=120)
st.title("🛡️ NeoGuard AI - Neonatal Risk Early Warning System")

st.markdown("""
AI-powered tool for predicting neonatal risk.  
Designed for **PHC workers, hospitals, and public health use**.
""")

# -----------------------
# Sidebar
# -----------------------
st.sidebar.title("Navigation")

input_mode = st.sidebar.radio(
    "Select Input Mode",
    ["Manual Entry", "Upload CSV"]
)

page = st.sidebar.selectbox(
    "Modules",
    ["Clinical Risk Assessment", "Population Dashboard", "National Risk Map", "Early Warning Alerts"]
)

# -----------------------
# Clinical Advice
# -----------------------
def clinical_advice(prob):
    if prob >= 0.7:
        return "🔴 HIGH RISK:\n- Immediate referral\n- Continuous monitoring\n- Prepare neonatal care"
    elif prob >= 0.4:
        return "🟡 MODERATE RISK:\n- Monitor closely\n- Increase ANC visits\n- Facility delivery advised"
    else:
        return "🟢 LOW RISK:\n- Routine care\n- Continue ANC visits"

# ============================
# MANUAL ENTRY
# ============================
if input_mode == "Manual Entry":

    if page == "Clinical Risk Assessment":

        st.subheader("Neonatal Risk Assessment")

        col1, col2 = st.columns(2)

        with col1:
            v012 = st.text_input("Mother's Age")
            v149 = st.selectbox("Education",
                ["No education","Incomplete Primary","Complete Primary","Incomplete Secondary","Complete Secondary","Higher"])
            v140 = st.selectbox("Residence", ["Urban", "Rural"])
            v190 = st.selectbox("Wealth Index",
                ["Poorest","Poorer","Middle","Richer","Richest"])
            b4 = st.selectbox("Child Sex", ["Male","Female"])
            bord = st.text_input("Birth Order")

        with col2:
            b11 = st.text_input("Birth Interval (months)")
            m15 = st.selectbox("Place of Delivery",
                ["Home","PHC","Hospital/Clinic"])
            m14 = st.text_input("ANC Visits")
            m1 = st.selectbox("Tetanus Protection", ["Yes","No"])
            b0 = st.selectbox("Multiple Birth", ["No","Yes"])
            m19 = st.text_input("Birth Weight (grams)")

        if st.button("Predict Risk"):

            user_input = {
                "v012": v012, "v149": v149, "v140": v140,
                "v190": v190, "b4": b4, "bord": bord,
                "b11": b11, "m15": m15, "m14": m14,
                "m1": m1, "b0": b0, "m19": m19
            }

            try:
                df = pd.DataFrame([user_input])
                df = preprocess_input(df)

                for col in features:
                    if col not in df.columns:
                        df[col] = 0

                df = df[features]

                prob = model.predict_proba(df)[0][1]

                # -----------------------
                # Result
                # -----------------------
                st.subheader("Risk Result")

                if prob >= 0.7:
                    st.error(f"🔴 HIGH RISK ({prob*100:.1f}%)")
                elif prob >= 0.4:
                    st.warning(f"🟡 MODERATE RISK ({prob*100:.1f}%)")
                else:
                    st.success(f"🟢 LOW RISK ({prob*100:.1f}%)")

                st.progress(float(prob))

                # -----------------------
                # Advice
                # -----------------------
                st.subheader("Clinical Recommendation")
                st.info(clinical_advice(prob))

                # -----------------------
                # Explainability
                # -----------------------
                st.subheader("Key Risk Factors")
                shap_single_plot(model, df)

            except Exception as e:
                st.error(f"Error: {e}")

    else:
        st.info("Manual entry works only in Clinical Risk Assessment")

# ============================
# CSV MODE
# ============================
elif input_mode == "Upload CSV":

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:

        df = pd.read_csv(uploaded_file)
        df = preprocess_input(df)

        for col in features:
            if col not in df.columns:
                df[col] = 0

        df = df[features]

        probs = model.predict_proba(df)[:, 1]
        df["risk_score"] = probs
        df["risk_class"] = df["risk_score"].apply(
            lambda x: "High Risk" if x >= 0.7 else ("Moderate Risk" if x >= 0.4 else "Low Risk")
        )

        if page == "Clinical Risk Assessment":

            st.dataframe(df.head())

            idx = st.number_input("Select Row", 0, len(df)-1, 0)

            case = df.iloc[[idx]]
            prob = case["risk_score"].values[0]

            if prob >= 0.7:
                st.error(f"🔴 HIGH RISK ({prob*100:.1f}%)")
            elif prob >= 0.4:
                st.warning(f"🟡 MODERATE RISK ({prob*100:.1f}%)")
            else:
                st.success(f"🟢 LOW RISK ({prob*100:.1f}%)")

            st.subheader("Clinical Recommendation")
            st.info(clinical_advice(prob))

            shap_single_plot(model, case)

        elif page == "Population Dashboard":

            st.bar_chart(df["risk_class"].value_counts())
            shap_summary_plot(model, df)

        elif page == "National Risk Map":

            fig = plot_national_risk(df, geojson_file="nigeria_states.geojson")
            st.plotly_chart(fig, use_container_width=True)

        elif page == "Early Warning Alerts":

            alerts = generate_alerts(df)
            st.warning(alerts)

    else:
        st.info("Upload a CSV file to continue.")
