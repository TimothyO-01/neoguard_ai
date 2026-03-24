
import pandas as pd
import numpy as np

def preprocess_input(df):
    df = df.copy()

    # Convert numeric fields properly
    numeric_cols = ["v012", "bord", "b11", "m14", "m19"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fill missing numeric
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Manual encoding (CONSISTENT with training)
    df["b4"] = df["b4"].map({"Male":1, "Female":0})
    df["v140"] = df["v140"].map({"Urban":1, "Rural":0})
    df["m1"] = df["m1"].map({"Yes":1, "No":0})
    df["b0"] = df["b0"].map({"Yes":1, "No":0})

    df["m15"] = df["m15"].map({
        "Home":0,
        "PHC":1,
        "Hospital/Clinic":2
    })

    df["v190"] = df["v190"].map({
        "Poorest":0,
        "Poorer":1,
        "Middle":2,
        "Richer":3,
        "Richest":4
    })

    df["v149"] = df["v149"].map({
        "No education":0,
        "Incomplete Primary":1,
        "Complete Primary":2,
        "Incomplete Secondary":3,
        "Complete Secondary":4,
        "Higher":5
    })

    return df
