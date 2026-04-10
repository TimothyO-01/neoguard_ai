import streamlit as st
import pandas as pd
import joblib

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from utils.preprocessing import preprocess_input
from utils.alerts import generate_alerts

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
    ["Clinical Risk Assessment", "Population Dashboard", "Early Warning Alerts"]
)

input_mode = st.sidebar.radio(
    "Input Mode",
    ["Manual Entry", "Batch Analysis (CSV)"]
)

# -----------------------
# TEMPLATE
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

st.sidebar.download_button(
    "Download CSV Template",
    sample_df.to_csv(index=False),
    "neoguard_template.csv",
    "text/csv"
)

# -----------------------
# FUNCTIONS
# -----------------------
def clinical_advice(prob):
    if prob >= 0.7:
        return "HIGH RISK: Immediate referral + monitoring"
    elif prob >= 0.4:
        return "MODERATE RISK: Close monitoring + ANC visits"
    else:
        return "LOW RISK: Routine care"

def explain_risk(data):
    reasons = []

    try:
        if float(data["BirthWeight"]) < 2500:
            reasons.append("Low birth weight")
    except:
        pass

    try:
        if float(data["ANC"]) < 4:
            reasons.append("Low ANC visits")
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
# PDF (SINGLE)
# -----------------------
def generate_pdf(result, prob, advice, factors):
    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("NeoGuard Clinical Report", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Risk: {result}", styles["Normal"]))
    story.append(Paragraph(f"Probability: {prob*100:.2f}%", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Recommendation", styles["Heading2"]))
    story.append(Paragraph(advice, styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Risk Factors", styles["Heading2"]))

    for f in factors:
        story.append(Paragraph(f"- {f}", styles["Normal"]))

    doc.build(story)

    with open("report.pdf", "rb") as f:
        return f.read()

# -----------------------
# PDF (BATCH)
# -----------------------
def generate_batch_pdf(df):
    doc = SimpleDocTemplate("batch_report.pdf")
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("NeoGuard Batch Report", styles["Title"]))
    story.append(Spacer(1, 12))

    total = len(df)
    high = len(df[df["risk_class"] == "High Risk"])
    moderate = len(df[df["risk_class"] == "Moderate Risk"])
    low = len(df[df["risk_class"] == "Low Risk"])

    story.append(Paragraph(f"Total: {total}", styles["Normal"]))
    story.append(Paragraph(f"High Risk: {high}", styles["Normal"]))
    story.append(Paragraph(f"Moderate: {moderate}", styles["Normal"]))
    story.append(Paragraph(f"Low: {low}", styles["Normal"]))
    story.append(Spacer(1, 12))

    display_df = df.head(20)
    table = Table([list(display_df.columns)] + display_df.values.tolist())

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))

    story.append(table)

    doc.build(story)

    with open("batch_report.pdf", "rb") as f:
        return f.read()

# ============================
# MANUAL MODE
# ============================
if input_mode == "Manual Entry":

    if page != "Clinical Risk Assessment":
        st.warning("Switch to Clinical Risk Assessment")
    else:
        st.subheader("Manual Risk Input")

        v012 = st.text_input("Mother Age")
        v149 = st.selectbox("Education", ["No education","Primary","Secondary","Higher"])
        v140 = st.selectbox("Residence", ["Urban","Rural"])
        v190 = st.selectbox("Wealth", ["Poorest","Poorer","Middle","Richer","Richest"])
        b4 = st.selectbox("Sex", ["Male","Female"])
        bord = st.text_input("Birth Order")

        b11 = st.text_input("Birth Interval")
        m15 = st.selectbox("Delivery Place", ["Home","PHC","Hospital"])
        m14 = st.text_input("ANC Visits")
        m1 = st.selectbox("Tetanus", ["Yes","No"])
        b0 = st.selectbox("Multiple Birth", ["No","Yes"])
        m19 = st.text_input("Birth Weight")

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

            result = "HIGH RISK" if prob >= 0.7 else "MODERATE RISK" if prob >= 0.4 else "LOW RISK"

            st.subheader(result)
            st.progress(prob)

            advice = clinical_advice(prob)
            st.info(advice)

            factors = explain_risk(user_input.iloc[0].to_dict())

            pdf = generate_pdf(result, prob, advice, factors)

            st.download_button(
                "Download Report",
                pdf,
                "neoguard_report.pdf",
                "application/pdf"
            )

# ============================
# BATCH MODE (FIXED STRUCTURE)
# ============================
elif input_mode == "Batch Analysis (CSV)":

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:

        raw_df = pd.read_csv(uploaded_file)

        df_processed = preprocess_input(raw_df.copy())

        for col in features:
            if col not in df_processed.columns:
                df_processed[col] = 0

        df_model = df_processed[features]

        raw_df["risk_score"] = model.predict_proba(df_model)[:, 1]

        raw_df["risk_class"] = raw_df["risk_score"].apply(
            lambda x: "High Risk" if x >= 0.7 else ("Moderate Risk" if x >= 0.4 else "Low Risk")
        )

        st.subheader("Results")
        st.dataframe(raw_df)

        st.subheader("High Risk Cases")
        st.dataframe(raw_df[raw_df["risk_class"] == "High Risk"])

        pdf_batch = generate_batch_pdf(raw_df)

        st.download_button(
            "Download Batch Report",
            pdf_batch,
            "neoguard_batch_report.pdf",
            "application/pdf"
        )

        if page == "Population Dashboard":
            st.bar_chart(raw_df["risk_class"].value_counts())

        elif page == "Early Warning Alerts":
            st.warning(generate_alerts(raw_df))

    else:
        st.info("Upload CSV to continue.")
