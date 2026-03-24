import shap
import streamlit as st
import matplotlib.pyplot as plt

def shap_summary_plot(model, X):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # Handle binary classification properly
    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    fig, ax = plt.subplots()
    shap.summary_plot(shap_values, X, show=False)
    st.pyplot(fig)


def shap_single_plot(model, X, feature_names):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # Fix shape issues
    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    # Convert to 1D safely
    shap_values = shap_values[0]

    fig, ax = plt.subplots()
    ax.barh(feature_names, shap_values)
    ax.set_title("Feature Contribution to Risk")

    st.pyplot(fig)
