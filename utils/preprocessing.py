import pandas as pd
import numpy as np

def preprocess_input(df):
    df = df.copy()

    # -----------------------
    # COLUMN STANDARDIZATION (NEW)
    # -----------------------
    rename_map = {
        "Age": "v012",
        "Education": "v149",
        "Residence": "v140",
        "Wealth": "v190",
        "Sex": "b4",
        "BirthOrder": "bord",
        "BirthInterval": "b11",
        "DeliveryPlace": "m15",
        "ANC": "m14",
        "Tetanus": "m1",
        "MultipleBirth": "b0",
        "BirthWeight": "m19"
    }

    df.rename(columns=rename_map, inplace=True)

    # -----------------------
    # ENSURE ALL REQUIRED COLUMNS EXIST
    # -----------------------
    required_cols = ["v012","v149","v140","v190","b4","bord","b11","m15","m14","m1","b0","m19"]

    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan

    # -----------------------
    # NUMERIC CONVERSION
    # -----------------------
    numeric_cols = ["v012", "bord", "b11", "m14", "m19"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df[numeric_cols] = df[numeric_cols].fillna(0)

    # -----------------------
    # ENCODING
    # -----------------------
    df["b4"] = df["b4"].map({"Male":1, "Female":0}).fillna(0)

    df["v140"] = df["v140"].map({
        "Urban":1,
        "Rural":0
    }).fillna(0)

    df["m1"] = df["m1"].map({
        "Yes":1,
        "No":0
    }).fillna(0)

    df["b0"] = df["b0"].map({
        "Yes":1,
        "No":0
    }).fillna(0)

    df["m15"] = df["m15"].map({
        "Home":0,
        "PHC":1,
        "Hospital/Clinic":2
    }).fillna(0)

    df["v190"] = df["v190"].map({
        "Poorest":0,
        "Poorer":1,
        "Middle":2,
        "Richer":3,
        "Richest":4
    }).fillna(0)

    df["v149"] = df["v149"].map({
        "No education":0,
        "Incomplete Primary":1,
        "Complete Primary":2,
        "Incomplete Secondary":3,
        "Complete Secondary":4,
        "Higher":5
    }).fillna(0)

    return df
