# NeoGuard - Neonatal Early Warning System

NeoGuard is an AI-powered neonatal risk prediction system designed for hospitals and primary healthcare centers. The platform provides early warning scores for newborns, interpretable risk factors, and recommendations for clinical action.

## Features
1. **AI-Based Risk Prediction**: Uses machine learning to predict neonatal mortality and complications.
2. **NeoGuard Risk Score**: Classifies newborns into Low, Moderate, or High risk.
3. **Clinical Decision Support**: Highlights key risk factors contributing to prediction.
4. **Explainable AI**: SHAP visualizations for global and individual patient explanations.
5. **Offline & Low-Resource Deployment**: Lightweight app for offline clinics or dashboards.

## Dataset
The model is trained on the 2024 Nigeria DHS dataset. **The dataset is not publicly included** due to licensing restrictions. You can access DHS data via [DHS Program](https://dhsprogram.com/).

## Model Training Results
**Confusion Matrix:**
[[ 42 141] [ 11 749]]

**Classification Report:**
- Precision: 0.79–0.84
- Recall: 0.23–0.99
- F1 Score: 0.36–0.91
- Accuracy: 0.84  
**AUC Score:** 0.939

Web: Streamlit Cloud

Offline:.py

Citations
DHS Program (2024), Nigeria Demographic and Health Survey.
