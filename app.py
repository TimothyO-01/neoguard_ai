import streamlit as st
import pandas as pd
import joblib
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from utils.preprocessing import preprocess_input
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
st.title("NeoGuard AI - Neonatal Risk Early Warning System")

st.markdown("""
AI-powered tool for predicting neonatal risk.  
Designed for **PHC workers, hospitals, and public health use**.
""")

# -----------------------
# Sidebar
# -----------------------
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Modules",
    ["Clinical Risk Assessment", "Population Dashboard", "National Risk Map", "Early Warning Alerts"]
)

input_mode = st.sidebar.radio(
    "Input Mode",
    ["Manual Entry", "Upload CSV"]
)

# -----------------------
# Clinical Advice
# -----------------------
def clinical_advice(prob):
    if prob >= 0.7:
        return "HIGH RISK:\n- Immediate referral\n- Continuous monitoring\n- Prepare neonatal care"
    elif prob >= 0.4:
        return "MODERATE RISK:\n- Monitor closely\n- Increase ANC visits\n- Facility delivery advised"
    else:
        return "LOW RISK:\n- Routine care\n- Continue ANC visits"

# -----------------------
# Rule-based Explanation
# -----------------------
def explain_risk(data):
    reasons = []

    if float(data["m19"]) < 2500:
        reasons.append("Low birth weight")

    if float(data["m14"]) < 4:
        reasons.append("Inadequate ANC visits")

    if data["m15"] == "Home":
        reasons.append("Home delivery")

    if float(data["b11"]) < 24:
        reasons.append("Short birth interval")

    if data["b0"] == "Yes":
        reasons.append("Multiple birth")

    return reasons

# -----------------------
# PDF Generator
# -----------------------
def generate_pdf(result, prob, advice, factors):
    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("NeoGuard AI Clinical Report", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Risk Level: {result}", styles["Normal"]))
    story.append(Paragraph(f"Probability: {prob*100:.2f}%", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Clinical Recommendation:", styles["Heading2"]))
    story.append(Paragraph(advice, styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Key Risk Factors:", styles["Heading2"]))
    for f in factors:
        story.append(Paragraph(f"- {f}", styles["Normal"]))

    doc.build(story)

    with open("report.pdf", "rb") as f:
        return f.read()

# ============================
# CLINICAL RISK (MANUAL)
# ============================
if page == "Clinical Risk Assessment" and input_mode == "Manual Entry":

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

        df = pd.DataFrame([user_input])
        df = preprocess_input(df)

        for col in features:
            if col not in df.columns:
                df[col] = 0

        df = df[features]

        prob = model.predict_proba(df)[0][1]

        # Result
        st.subheader("Risk Result")

        if prob >= 0.7:
            result = "HIGH RISK"
            st.error(f"{result} ({prob*100:.1f}%)")
        elif prob >= 0.4:
            result = "MODERATE RISK"
            st.warning(f"{result} ({prob*100:.1f}%)")
        else:
            result = "LOW RISK"
            st.success(f"{result} ({prob*100:.1f}%)")

        st.progress(float(prob))

        # Advice
        advice = clinical_advice(prob)
        st.subheader("Clinical Recommendation")
        st.info(advice)

        # Explanation
        factors = explain_risk(user_input)
        st.subheader("Key Risk Factors")

        if factors:
            for f in factors:
                st.write(f"• {f}")
        else:
            st.write("No major risk factors detected")

        # PDF Download
        pdf = generate_pdf(result, prob, advice, factors)

        st.download_button(
            label="Download Clinical Report",
            data=pdf,
            file_name="neoguard_report.pdf",
            mime="application/pdf"
        )

# ============================
# CSV MODE (ALL MODULES)
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

        df["risk_score"] = model.predict_proba(df)[:, 1]
        df["risk_class"] = df["risk_score"].apply(
            lambda x: "High Risk" if x >= 0.7 else ("Moderate Risk" if x >= 0.4 else "Low Risk")
        )

        if page == "Population Dashboard":
            st.bar_chart(df["risk_class"].value_counts())

        elif page == "National Risk Map":
            fig = plot_national_risk(df, geojson_file="nigeria_states.geojson")
            st.plotly_chart(fig, use_container_width=True)

        elif page == "Early Warning Alerts":
            st.warning(generate_alerts(df))

    else:
        st.info("Upload a CSV file to continue.")

# ============================
# BLOCK INVALID COMBINATIONS
# ============================
else:
    st.warning("This module requires CSV upload.")
