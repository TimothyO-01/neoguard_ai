
import shap
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def shap_single_plot(model, X, feature_names):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # Fix for binary classification
    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    shap_values = shap_values[0]

    # match feature length
    min_len = min(len(feature_names), len(shap_values))
    shap_values = shap_values[:min_len]
    feature_names = feature_names[:min_len]

    fig, ax = plt.subplots()
    ax.barh(feature_names, shap_values)
    ax.set_title("Feature Contribution to Risk")

    st.pyplot(fig)
