
import shap
import streamlit as st
import matplotlib.pyplot as plt

def shap_single_plot(model, X):
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)

        # For binary classification
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        shap_values = shap_values[0]

        feature_names = X.columns.tolist()

        fig, ax = plt.subplots(figsize=(6,4))
        ax.barh(feature_names, shap_values)
        ax.set_title("Key Factors Influencing Risk")

        st.pyplot(fig)

    except Exception as e:
        st.warning("SHAP explanation not available on this device")


def shap_summary_plot(model, X):
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)

        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        fig = plt.figure()
        shap.summary_plot(shap_values, X, show=False)

        st.pyplot(fig)

    except Exception:
        st.warning("Summary plot unavailable")
