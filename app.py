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
# PDF
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

# -----------------------
# TEMPLATE DOWNLOAD (NEW)
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

st.sidebar.download_button("Download CSV Template", csv_template, "template.csv")

# ============================
# MANUAL ENTRY
# ============================
if input_mode == "Manual Entry" and page == "Clinical Risk Assessment":

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

        if prob >= 0.7:
            result = "HIGH RISK"
            st.error(result)
        elif prob >= 0.4:
            result = "MODERATE RISK"
            st.warning(result)
        else:
            result = "LOW RISK"
            st.success(result)

        st.progress(float(prob))

# ============================
# CSV MODE (UPGRADED)
# ============================
elif input_mode == "Batch Analysis (CSV)":

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

        st.subheader("Batch Results")
        st.dataframe(df)

        st.subheader("High Risk Cases")
        st.dataframe(df[df["risk_class"] == "High Risk"])

        if page == "Population Dashboard":
            st.bar_chart(df["risk_class"].value_counts())

        elif page == "National Risk Map":
            fig = plot_national_risk(df, geojson_file="nigeria_states.geojson")
            st.plotly_chart(fig, use_container_width=True)

        elif page == "Early Warning Alerts":
            st.warning(generate_alerts(df))

    else:
        st.info("Upload a CSV file to continue.")

else:
    st.info("Manual entry is only available for Clinical Risk Assessment.")
