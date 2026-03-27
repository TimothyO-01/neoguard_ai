import streamlit as st
import pandas as pd
import joblib
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from utils.preprocessing import preprocess_input
from utils.alerts import generate_alerts, plot_national_risk

# -----------------------
# LOAD MODEL
# -----------------------
model = joblib.load("model/neoguard_model.pkl")
features = joblib.load("model/neoguard_features.pkl")

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(page_title="NeoGuard AI", layout="wide", page_icon="🛡️")

st.image("asset/logos.png", width=120)
st.title("NeoGuard AI - Neonatal Risk Early Warning System")

st.markdown("""
AI-powered tool for predicting neonatal risk.  
Designed for **PHC workers, hospitals, and public health use**.
""")

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Modules",
    ["Clinical Risk Assessment", "Population Dashboard", "National Risk Map", "Early Warning Alerts"]
)

input_mode = st.sidebar.radio(
    "Input Mode",
    ["Manual Entry", "Batch Analysis (CSV)"]
)

# -----------------------
# TEMPLATE DOWNLOAD
# -----------------------
sample_df = pd.DataFrame({
    "Age":[25],
    "Education":["No education"],
    "Residence":["Rural"],
    "Wealth":["Poorest"],
    "Sex":["Male"],
    "BirthOrder":[1],
    "BirthInterval":[12],
    "DeliveryPlace":["Home"],
    "ANC":[2],
    "Tetanus":["No"],
    "MultipleBirth":["No"],
    "BirthWeight":[1800]
})

csv_template = sample_df.to_csv(index=False)

st.sidebar.download_button(
    "Download CSV Template",
    csv_template,
    "neoguard_template.csv",
    "text/csv"
)

# -----------------------
# CLINICAL FUNCTIONS
# -----------------------
def clinical_advice(prob):
    if prob >= 0.7:
        return "HIGH RISK:\n Immediate referral\n Continuous monitoring\n Prepare neonatal care"
    elif prob >= 0.4:
        return "MODERATE RISK:\n Monitor closely\n Increase Antenatal Care visits\n Facility delivery advised"
    else:
        return "LOW RISK:\n Routine care\n Continue Antenatal Care visits"

def explain_risk(data):
    reasons = []

    try:
        if float(data["BirthWeight"]) < 2500:
            reasons.append("Low birth weight")
    except:
        pass

    try:
        if float(data["ANC"]) < 4:
            reasons.append("Inadequate Antenatal Care visits")
    except:
        pass

    if data["DeliveryPlace"] == "Home":
        reasons.append("Home delivery")

    try:
        if float(data["BirthInterval"]) < 24:
            reasons.append("Short birth interval")
    except:
        pass

    if data["MultipleBirth"] == "Yes":
        reasons.append("Multiple birth")

    return reasons

# -----------------------
# PDF GENERATOR
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
# MANUAL ENTRY
# ============================
if input_mode == "Manual Entry":

    if page != "Clinical Risk Assessment":
        st.warning("Manual entry works only in Clinical Risk Assessment")

    else:
        st.subheader("Neonatal Risk Assessment")

        col1, col2 = st.columns(2)

        with col1:
            v012 = st.text_input("Mother Age")
            v149 = st.selectbox("Education", ["No education","Incomplete Primary","Complete Primary","Incomplete Secondary","Complete Secondary","Higher"])
            v140 = st.selectbox("Residence", ["Urban","Rural"])
            v190 = st.selectbox("Wealth", ["Poorest","Poorer","Middle","Richer","Richest"])
            b4 = st.selectbox("Sex", ["Male","Female"])
            bord = st.text_input("Birth Order")

        with col2:
            b11 = st.text_input("Birth Interval")
            m15 = st.selectbox("Delivery Place", ["Home","PHC","Hospital/Clinic"])
            m14 = st.text_input("Antenatal Care Visits")
            m1 = st.selectbox("Tetanus Protection", ["Yes","No"])
            b0 = st.selectbox("Multiple Birth", ["No","Yes"])
            m19 = st.text_input("Birth Weight (grams)")

        if st.button("Predict Risk"):

            user_input = pd.DataFrame([{
                "Age": v012,
                "Education": v149,
                "Residence": v140,
                "Wealth": v190,
                "Sex": b4,
                "BirthOrder": bord,
                "BirthInterval": b11,
                "DeliveryPlace": m15,
                "ANC": m14,
                "Tetanus": m1,
                "MultipleBirth": b0,
                "BirthWeight": m19
            }])

            df = preprocess_input(user_input)

            for col in features:
                if col not in df.columns:
                    df[col] = 0

            df = df[features]

            prob = model.predict_proba(df)[0][1]

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
            factors = explain_risk({
                "BirthWeight": m19,
                "ANC": m14,
                "DeliveryPlace": m15,
                "BirthInterval": b11,
                "MultipleBirth": b0
            })

            st.subheader("Key Risk Factors")

            if factors:
                for f in factors:
                    st.write(f"• {f}")
            else:
                st.write("No major risk factors detected")

            # PDF
            pdf = generate_pdf(result, prob, advice, factors)

            st.download_button(
                "Download Clinical Report",
                pdf,
                "neoguard_report.pdf",
                "application/pdf"
            )

# ============================
# CSV MODE
# ============================
elif input_mode == "Batch Analysis (CSV)":

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:

        raw_df = pd.read_csv(uploaded_file)

        df = preprocess_input(raw_df)

        for col in features:
            if col not in df.columns:
                df[col] = 0

        df_model = df[features]

        df["risk_score"] = model.predict_proba(df_model)[:, 1]
        df["risk_class"] = df["risk_score"].apply(
            lambda x: "High Risk" if x >= 0.7 else ("Moderate Risk" if x >= 0.4 else "Low Risk")
        )

        st.subheader("Batch Results")
        st.dataframe(df)

        st.subheader("High Risk Cases")
        st.dataframe(df[df["risk_class"] == "High Risk"])

        # DOWNLOAD CSV RESULTS
        result_csv = df.to_csv(index=False)

        st.download_button(
            "Download Patient Results (CSV)",
            result_csv,
            "neoguard_results.csv",
            "text/csv"
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
