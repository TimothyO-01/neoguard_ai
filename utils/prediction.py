
import numpy as np

def predict_risk(model, df):
    pred_prob = model.predict_proba(df)[:, 1]
    
    if pred_prob[0] >= 0.5:
        pred_class = "High Risk"
    else:
        pred_class = "Low/Moderate Risk"
        
    return pred_class, float(pred_prob[0])
