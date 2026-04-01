**NeoGuard AI - Neonatal Risk Early Warning System**

**Overview**

NeoGuard AI is a machine learning-powered clinical decision support tool designed to predict neonatal risk using maternal, socioeconomic, and birth-related factors.

It is built to support:
- Primary Health Care (PHC) workers
- Hospitals and clinicians
- Public health analysts

The goal is to enable early detection of high-risk neonates and reduce preventable neonatal mortality.

**Problem Statement**

Neonatal mortality remains a major global health challenge, especially in low- and middle-income countries like Nigeria.
Many high-risk cases are:
- Detected late
- Poorly monitored
- Not referred in time
  
This leads to preventable deaths.

**Solution**

NeoGuard AI provides:
- Real-time risk prediction
- Clinical recommendations
- Population-level insights
- Early warning alerts

**How It Works**

1. Input Data: The model uses key predictors such as:Maternal ageAntenatal care visitsBirth intervalBirth weightDelivery locationSocioeconomic indicators
2. Processing: Data is cleaned and encodedFeatures aligned with trained model
3. Prediction: Outputs risk probability (0–1)
4. Classifies into:- Low Risk
   - Moderate Risk
   - High Risk
5. Output:- Clinical recommendations
   - Key risk factor explanations
   - Downloadable PDF reports
   - Batch analysis for multiple patients

**NeoGuard Features**

**Clinical Risk Assessment**
- Manual patient input
- Instant prediction
- Actionable recommendations

**Batch Analysis (CSV Upload)** 
- Analyze multiple patients
- Download results
- Identify high-risk groups

**Population Dashboard**
- Risk distribution visualization

**Early Warning Alerts**
- Detects spikes in high-risk cases
- Generates actionable alerts

**Dataset**

This project is based on data inspired by the Demographic and Health Surveys (DHS).

**DHS Reference**

The DHS Program provides nationally representative data at https://dhsprogram.com

**Tech Stack**
- Python
- Streamlit (Frontend)
- Scikit-learn (Modeling)
- Pandas / NumPy (Data processing)
- Plotly (Visualization)
- ReportLab (PDF generation)
  
**Model Classification Model**
Output: **Probability of neonatal risk**

Thresholds:

- ≥ 0.7 → High Risk
- 0.4–0.69 → Moderate Risk
- < 0.4 → Low Risk
  
**Installation**

git clone https://github.com/yourusername/neoguard_ai.git

cd neoguard-ai

pip install -r requirements.txt streamlit 

run app.py

**Usage**

**Manual Mode**
- Enter patient details
- Click Predict Risk
  
**CSV Mode**
  - Upload template
  - View batch predictions
  - Download results
    
 **Output Example**
 - Risk classification
 - Probability score
 - Clinical advice
 - Risk factor explanation
 - PDF report
   
 **Limitations**
 NeoGuard is not a substitute for clinical judgment. It requires validation on real-world hospital dataModel performance depends on data quality
 
**Future Improvements**
- Integration with hospital EMR systems
- Real-time national surveillance dashboard
- Explainable AI
- Mobile app deployment
  
Live app: https://neoguardai.streamlit.app/
