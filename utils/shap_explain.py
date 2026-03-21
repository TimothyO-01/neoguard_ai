import shap
import matplotlib.pyplot as plt
import streamlit as st

def shap_summary_plot(model, features):
    explainer = shap.TreeExplainer(model)
    # Dummy data for summary (use model training data ideally)
    shap_values = explainer.shap_values(model._Booster)
    st.pyplot(shap.summary_plot(shap_values, features, show=False))

def shap_single_plot(model, input_df, features):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(input_df)
    st.pyplot(shap.force_plot(explainer.expected_value[1], shap_values[1], input_df, matplotlib=True))
