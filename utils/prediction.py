import numpy as np

def predict_risk(model, df):
    """Predicts neonatal risk and returns class and probability."""
    pred_prob = model.predict_proba(df)[:,1]
    pred_class = np.where(pred_prob > 0.5, "High Risk", "Low/Moderate Risk")[0]
    return pred_class, pred_prob[0]
