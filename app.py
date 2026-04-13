import streamlit as st      
import pandas as pd      
import joblib      
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer      
from reportlab.lib.styles import getSampleStyleSheet      
      
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
        return "HIGH RISK:\n- Immediate referral\n- Continuous monitoring\n- Prepare neonatal care"      
    elif prob >= 0.4:      
        return "MODERATE RISK:\n- Monitor closely\n- Increase ANC visits\n- Facility delivery advised"      
    else:      
        return "LOW RISK:\n- Routine care\n- Continue ANC visits"      
      
def explain_risk(data):      
    reasons = []      
    try:      
        if float(data["BirthWeight"]) < 2500:      
            reasons.append("Low birth weight")      
    except: pass      
      
    try:      
        if float(data["ANC"]) < 4:      
            reasons.append("Inadequate Antenatal Care visits")      
    except: pass      
      
    if data["DeliveryPlace"] == "Home":      
        reasons.append("Home delivery")      
      
    try:      
        if float(data["BirthInterval"]) < 24:      
            reasons.append("Short birth interval")      
    except: pass      
      
    if data["MultipleBirth"] == "Yes":      
        reasons.append("Multiple birth")      
      
    return reasons      
      
# -----------------------      
# FIXED PDF (INDIVIDUAL)      
# -----------------------      
def generate_pdf(result, prob, advice, factors):      
    buffer = BytesIO()      
    doc = SimpleDocTemplate(buffer)      
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
    buffer.seek(0)      
    return buffer      
      
# -----------------------      
# FIXED PDF (POPULATION)      
# -----------------------      
def generate_population_pdf(df, page):      
    buffer = BytesIO()      
    doc = SimpleDocTemplate(buffer)      
    styles = getSampleStyleSheet()      
    story = []      
      
    story.append(Paragraph("NeoGuard AI Population Health Report", styles["Title"]))      
    story.append(Spacer(1, 12))      
      
    total = len(df)      
    high = len(df[df["risk_class"] == "High Risk"])      
    moderate = len(df[df["risk_class"] == "Moderate Risk"])      
    low = len(df[df["risk_class"] == "Low Risk"])      
      
    story.append(Paragraph(f"Total Patients: {total}", styles["Normal"]))      
    story.append(Paragraph(f"High Risk: {high}", styles["Normal"]))      
    story.append(Paragraph(f"Moderate Risk: {moderate}", styles["Normal"]))      
    story.append(Paragraph(f"Low Risk: {low}", styles["Normal"]))      
    story.append(Spacer(1, 12))      
      
    if page == "Population Dashboard":      
        story.append(Paragraph("Population Distribution Summary", styles["Heading2"]))      
        for k, v in df["risk_class"].value_counts().items():      
            story.append(Paragraph(f"{k}: {v}", styles["Normal"]))      
      
    elif page == "Early Warning Alerts":      
        story.append(Paragraph("Early Warning Alerts Summary", styles["Heading2"]))      
        story.append(Paragraph(str(generate_alerts(df)), styles["Normal"]))      
      
    elif page == "Clinical Risk Assessment":      
        story.append(Paragraph("Batch Clinical Overview", styles["Heading2"]))      
        story.append(Paragraph("Batch processed using NeoGuard AI model.", styles["Normal"]))      
      
    doc.build(story)      
    buffer.seek(0)      
    return buffer      
      
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
            b11 = st.text_input("Birth Interval (months)")      
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
      
            advice = clinical_advice(prob)      
            st.info(advice)      
      
            factors = explain_risk({      
                "BirthWeight": m19,      
                "ANC": m14,      
                "DeliveryPlace": m15,      
                "BirthInterval": b11,      
                "MultipleBirth": b0      
            })      
      
            pdf = generate_pdf(result, prob, advice, factors)      
      
            st.download_button(      
                "Download Clinical Report",      
                pdf,      
                "neoguard_report.pdf",      
                "application/pdf"      
            )      

# ============================
# CSV MODE (ROBUST VERSION)
# ============================
elif input_mode == "Batch Analysis (CSV)":
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        try:
            raw_df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            st.stop()

        # -----------------------
        # VALIDATE REQUIRED COLUMNS
        # -----------------------
        required_columns = [
            "Age","Education","Residence","Wealth","Sex",
            "BirthOrder","BirthInterval","DeliveryPlace",
            "ANC","Tetanus","MultipleBirth","BirthWeight"
        ]

        # Clean column names (remove spaces)
        raw_df.columns = raw_df.columns.str.strip()

        missing = [col for col in required_columns if col not in raw_df.columns]

        if missing:
            st.error(f"Missing required columns: {missing}")
            st.stop()

        # -----------------------
        # FIX DATA TYPES
        # -----------------------
        numeric_cols = ["Age", "BirthOrder", "BirthInterval", "ANC", "BirthWeight"]

        for col in numeric_cols:
            raw_df[col] = pd.to_numeric(raw_df[col], errors="coerce")

        # -----------------------
        # PREPROCESS SAFELY
        # -----------------------
        try:
            df_processed = preprocess_input(raw_df.copy())
        except Exception as e:
            st.error(f"Preprocessing error: {e}")
            st.stop()

        # -----------------------
        # ENSURE FEATURE ALIGNMENT
        # -----------------------
        df_model = df_processed.reindex(columns=features, fill_value=0)

        # Handle missing values
        df_model = df_model.fillna(0)

        # -----------------------
        # MODEL PREDICTION
        # -----------------------
        try:
            raw_df["risk_score"] = model.predict_proba(df_model)[:, 1]
        except Exception as e:
            st.error(f"Prediction error: {e}")
            st.stop()

        raw_df["risk_class"] = raw_df["risk_score"].apply(
            lambda x: "High Risk" if x >= 0.7 else (
                "Moderate Risk" if x >= 0.4 else "Low Risk"
            )
        )

        # -----------------------
        # DISPLAY RESULTS
        # -----------------------
        st.subheader("Patient Results")

        if len(raw_df) > 1000:
            st.warning(f"Large dataset detected ({len(raw_df)} rows). Showing first 100 rows only.")
            st.dataframe(raw_df.head(100))
        else:
            st.dataframe(raw_df)

        # -----------------------
        # HIGH RISK CASES
        # -----------------------
        st.subheader("High Risk Cases")
        high_risk_df = raw_df[raw_df["risk_class"] == "High Risk"]

        if len(high_risk_df) == 0:
            st.success("No high-risk cases detected 🎉")
        else:
            st.dataframe(high_risk_df)

        # -----------------------
        # PDF GENERATION (SAFE)
        # -----------------------
        if len(raw_df) > 2000:
            st.warning("PDF will include summary only due to large dataset.")

        pdf = generate_population_pdf(raw_df, page)

        st.download_button(
            "Download Population Health Report (PDF)",
            pdf,
            "neoguard_population_report.pdf",
            "application/pdf"
        )

        # -----------------------
        # VISUALIZATION
        # -----------------------
        if page == "Population Dashboard":
            st.bar_chart(raw_df["risk_class"].value_counts())

        elif page == "Early Warning Alerts":
            st.warning(generate_alerts(raw_df))

    else:
        st.info("Upload a CSV file to continue.")
