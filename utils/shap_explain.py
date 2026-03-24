
import shap
import streamlit as st
import matplotlib.pyplot as plt

def shap_summary_plot(model, X):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    fig, ax = plt.subplots()
    shap.summary_plot(shap_values, X, show=False)
    st.pyplot(fig)


def shap_single_plot(model, X, feature_names):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    fig, ax = plt.subplots()
    shap.bar_plot(shap_values[0], feature_names=feature_names)
    st.pyplot(fig)
