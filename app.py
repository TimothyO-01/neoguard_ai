import streamlit as st
import pandas as pd
import joblib
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from utils.preprocessing import preprocess_input
from utils.alerts import generate_alerts

# ============================
# LOAD MODEL
# ============================
model = joblib.load("model/neoguard_model.pkl")
features = joblib.load("model/neoguard_features.pkl")

# ============================
# CONFIG
# ============================
st.set_page_config(page_title="NeoGuard AI", layout="wide", page_icon="🛡️")

st.image("asset/logos.png", width=120)
st.title("NeoGuard AI - Neonatal Risk Early Warning System")

st.markdown("""
AI-powered tool for predicting neonatal risk.  
Designed for **PHC workers, hospitals, and public health use**.
""")

# ============================
# SIDEBAR
# ============================
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Modules",
    ["Clinical Risk Assessment", "Population Dashboard", "Early Warning Alerts"]
)

input_mode = st.sidebar.radio(
    "Input Mode",
    ["Manual Entry", "Batch Analysis (CSV)"]
)

# ============================
# TEMPLATE
# ============================
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

# ============================
# FUNCTIONS
# ============================
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


def generate_pdf(result, prob, advice, factors):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("NeoGuard AI Report", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Risk: {result}", styles["Normal"]))
    story.append(Paragraph(f"Probability: {prob*100:.2f}%", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Advice:", styles["Heading2"]))
    story.append(Paragraph(advice, styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Risk Factors:", styles["Heading2"]))
    for f in factors:
        story.append(Paragraph(f"- {f}", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_population_pdf(df, page):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("NeoGuard Population Report", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Total: {len(df)}", styles["Normal"]))
    story.append(Paragraph(f"High Risk: {len(df[df['risk_class']=='High Risk'])}", styles["Normal"]))
    story.append(Paragraph(f"Moderate Risk: {len(df[df['risk_class']=='Moderate Risk'])}", styles["Normal"]))
    story.append(Paragraph(f"Low Risk: {len(df[df['risk_class']=='Low Risk'])}", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================
# MANUAL MODE (GROUPED UI)
# ============================
if input_mode == "Manual Entry":

    if page != "Clinical Risk Assessment":
        st.warning("Manual entry only works in Clinical Risk Assessment")

    else:
        st.subheader("Clinical Risk Assessment")

        # ============================
        # SECTION 1: MOTHER PROFILE
        # ============================
        st.markdown("### Mother’s Profile")
        st.caption("Basic background information about the mother")

        col1, col2 = st.columns(2)

        with col1:
            age = st.text_input("Age", placeholder="e.g. 25")
            edu = st.selectbox(
                "Education",
                ["No education","Primary","Secondary","Higher"],
                help="Highest level of education"
            )
            res = st.selectbox(
                "Residence",
                ["Urban","Rural"],
                help="Place of residence"
            )

        with col2:
            wealth = st.selectbox(
                "Wealth",
                ["Poorest","Poorer","Middle","Richer","Richest"],
                help="Socioeconomic level"
            )
            sex = st.selectbox("Sex", ["Male","Female"])
            order = st.text_input("Birth Order", placeholder="e.g. 1")

        st.divider()

        # ============================
        # SECTION 2: PREGNANCY HISTORY
        # ============================
        st.markdown("### Pregnancy History")
        st.caption("Details about antenatal care and pregnancy conditions")

        col1, col2 = st.columns(2)

        with col1:
            interval = st.text_input(
                "Birth Interval (months)",
                placeholder="e.g. 12"
            )
            place = st.selectbox(
                "Delivery Place",
                ["Home","PHC","Hospital"],
                help="Where delivery occurred"
            )
            anc = st.text_input(
                "Antenatal Visits",
                placeholder="e.g. 4"
            )

        with col2:
            tetanus = st.selectbox(
                "Tetanus",
                ["Yes","No"],
                help="Tetanus immunization status"
            )
            multi = st.selectbox(
                "Multiple Birth",
                ["No","Yes"],
                help="Twins or more"
            )

        st.divider()

        # ============================
        # SECTION 3: NEWBORN DETAILS
        # ============================
        st.markdown("### Newborn Details")
        st.caption("Information about the baby at birth")

        col1, col2 = st.columns(2)

        with col1:
            weight = st.text_input(
                "Birth Weight (grams)",
                placeholder="e.g. 2500"
            )

        with col2:
            st.markdown(" ")  # spacing

        st.divider()

        # ============================
        # PREDICTION BUTTON
        # ============================
        if st.button("Predict Risk"):

            user_input = pd.DataFrame([{
                "Age": age,
                "Education": edu,
                "Residence": res,
                "Wealth": wealth,
                "Sex": sex,
                "BirthOrder": order,
                "BirthInterval": interval,
                "DeliveryPlace": place,
                "ANC": anc,
                "Tetanus": tetanus,
                "MultipleBirth": multi,
                "BirthWeight": weight
            }])

            df = preprocess_input(user_input)
            df = df.reindex(columns=features, fill_value=0)

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
# MANUAL MODE
# ============================
if input_mode == "Manual Entry":

    if page != "Clinical Risk Assessment":
        st.warning("Manual entry only works in Clinical Risk Assessment")

    else:
        st.subheader("Clinical Risk Assessment")

        col1, col2 = st.columns(2)

        with col1:
            age = st.text_input("Age")
            edu = st.selectbox("Education", ["No education","Primary","Secondary","Higher"])
            res = st.selectbox("Residence", ["Urban","Rural"])
            wealth = st.selectbox("Wealth", ["Poorest","Poorer","Middle","Richer","Richest"])
            sex = st.selectbox("Sex", ["Male","Female"])
            order = st.text_input("Birth Order")

        with col2:
            interval = st.text_input("Birth Interval")
            place = st.selectbox("Delivery Place", ["Home","PHC","Hospital"])
            anc = st.text_input("ANC Visits")
            tetanus = st.selectbox("Tetanus", ["Yes","No"])
            multi = st.selectbox("Multiple Birth", ["No","Yes"])
            weight = st.text_input("Birth Weight")

        if st.button("Predict Risk"):

            user_input = pd.DataFrame([{
                "Age": age,
                "Education": edu,
                "Residence": res,
                "Wealth": wealth,
                "Sex": sex,
                "BirthOrder": order,
                "BirthInterval": interval,
                "DeliveryPlace": place,
                "ANC": anc,
                "Tetanus": tetanus,
                "MultipleBirth": multi,
                "BirthWeight": weight
            }])

            df = preprocess_input(user_input)
            df = df.reindex(columns=features, fill_value=0)

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
# CSV MODE (FIXED)
# ============================
elif input_mode == "Batch Analysis (CSV)":

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:

        try:
            raw_df = pd.read_csv(uploaded_file)
            raw_df.columns = raw_df.columns.str.strip()

        except Exception as e:
            st.error(f"CSV error: {e}")
            st.stop()

        required = [
            "Age","Education","Residence","Wealth","Sex",
            "BirthOrder","BirthInterval","DeliveryPlace",
            "ANC","Tetanus","MultipleBirth","BirthWeight"
        ]

        missing = [c for c in required if c not in raw_df.columns]

        if missing:
            st.error(f"Missing columns: {missing}")
            st.stop()

        numeric = ["Age","BirthOrder","BirthInterval","ANC","BirthWeight"]

        for c in numeric:
            raw_df[c] = pd.to_numeric(raw_df[c], errors="coerce")

        try:
            df_processed = preprocess_input(raw_df.copy())
        except Exception as e:
            st.error(f"Preprocess error: {e}")
            st.stop()

        df_model = df_processed.reindex(columns=features, fill_value=0)
        df_model = df_model.fillna(0)

        try:
            probs = model.predict_proba(df_model)[:, 1]
        except Exception as e:
            st.error(f"Prediction error: {e}")
            st.stop()

        raw_df["risk_score"] = probs

        raw_df["risk_class"] = raw_df["risk_score"].apply(
            lambda x: "High Risk" if x >= 0.7 else (
                "Moderate Risk" if x >= 0.4 else "Low Risk"
            )
        )

        st.subheader("Results")
        st.dataframe(raw_df.head(200))

        st.subheader("High Risk Cases")
        st.dataframe(raw_df[raw_df["risk_class"] == "High Risk"])

        if page == "Population Dashboard":
            st.bar_chart(raw_df["risk_class"].value_counts())

        elif page == "Early Warning Alerts":
            st.warning(generate_alerts(raw_df))

        pdf = generate_population_pdf(raw_df, page)

        st.download_button(
            "Download Report",
            pdf,
            "neoguard_population_report.pdf",
            "application/pdf"
        )

    else:
        st.info("Upload a CSV file to continue.")
