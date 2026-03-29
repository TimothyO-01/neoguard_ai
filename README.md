**NeoGuard AI - Neonatal Risk Early Warning System**

**Overview**
NeoGuard AI is a machine learning-powered clinical decision support tool designed to predict neonatal risk using maternal, socioeconomic, and birth-related factors.
It is built to support:Primary Health Care (PHC) workersHospitals and cliniciansPublic health analysts

The goal is to:Enable early detection of high-risk neonates and reduce preventable neonatal mortality.

**Problem Statement**
Neonatal mortality remains a major global health challenge, especially in low- and middle-income countries like Nigeria.
Many high-risk cases are:
Detected late
Poorly monitored
Not referred in time
This leads to preventable deaths.

**Solution**
NeoGuard AI provides:
Real-time risk prediction
Clinical recommendations
Population-level insights
Early warning alerts

**How It Works**
1. Input Data The model uses key predictors such as:Maternal ageAntenatal care visitsBirth intervalBirth weightDelivery locationSocioeconomic indicators
2. ProcessingData is cleaned and encodedFeatures aligned with trained model
3. PredictionOutputs risk probability (0–1)Classifies into:Low RiskModerate RiskHigh Risk
4. OutputClinical recommendationsKey risk factor explanationsDownloadable PDF reportsBatch analysis for multiple patients

**NeoGuard Features**
Clinical Risk Assessment

**Manual patient input**
Instant prediction
Actionable recommendations

**Batch Analysis (CSV Upload)** 
Analyze multiple patients
Download results
Identify high-risk groups

**Population Dashboard**
Risk distribution visualization

**Early Warning Alerts**
Detects spikes in high-risk cases
Generates actionable alerts
Dataset This project is based on data inspired by the Demographic and Health Surveys (DHS).
DHS ReferenceThe DHS Program provides nationally representative data at https://dhsprogram.com
Tech StackPythonStreamlit (Frontend)Scikit-learn (Modeling)Pandas / NumPy (Data processing)Plotly (Visualization)ReportLab (PDF generation)
ModelClassification Model
Output: Probability of neonatal risk
Thresholds:≥ 0.7 → High Risk0.4–0.69 → Moderate Risk< 0.4 → Low Risk
Installationgit clone https://github.com/yourusername/neoguard_ai.gitcd neoguard-aipip install -r requirements.txtstreamlit run app.py
Usage
Manual ModeEnter patient detailsClick Predict Risk
CSV ModeUpload templateView batch predictionsDownload results
 Output ExampleRisk classificationProbability scoreClinical adviceRisk factor explanationPDF report
 LimitationsNot a substitute for clinical judgmentRequires validation on real-world hospital dataModel performance depends on data quality
Future ImprovementsIntegration with hospital EMR systemsReal-time national surveillance dashboardExplainable AI (SHAP visualization)Mobile app deployment
 ContributionContributions are welcome!
Links GitHub: https://github.com/TimothyO-01/neoguard_ai/Live app: https://neoguardai.streamlit.app/
