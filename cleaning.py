import pandas as pd
import numpy as np

# -----------------------------
# COLUMN NORMALIZATION MAP
# -----------------------------
COLUMN_ALIASES = {
    "age": "Age",
    "mother age": "Age",
    "v012": "Age",

    "education": "Education",
    "mother education": "Education",
    "v149": "Education",

    "residence": "Residence",
    "v140": "Residence",

    "wealth": "Wealth",
    "v190": "Wealth",

    "sex": "Sex",
    "gender": "Sex",
    "b4": "Sex",

    "birth order": "BirthOrder",
    "birthorder": "BirthOrder",
    "bord": "BirthOrder",

    "birth interval": "BirthInterval",
    "birthinterval": "BirthInterval",
    "b11": "BirthInterval",

    "delivery place": "DeliveryPlace",
    "delivery": "DeliveryPlace",
    "m15": "DeliveryPlace",

    "anc": "ANC",
    "antenatal visits": "ANC",
    "m14": "ANC",

    "tetanus": "Tetanus",
    "m1": "Tetanus",

    "multiple birth": "MultipleBirth",
    "twins": "MultipleBirth",
    "b0": "MultipleBirth",

    "birth weight": "BirthWeight",
    "birthweight": "BirthWeight",
    "m19": "BirthWeight",
}


# -----------------------------
# MAIN CLEANING FUNCTION
# -----------------------------
def clean_csv(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    # 2. Rename using alias map
    df.rename(columns=lambda x: COLUMN_ALIASES.get(x, x), inplace=True)

    # 3. Strip string values
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    # 4. Fix numeric columns safely
    numeric_cols = ["Age", "BirthOrder", "BirthInterval", "ANC", "BirthWeight"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Fill missing values
    df = df.replace(["nan", "None", ""], np.nan)
    df.fillna(0, inplace=True)

    # 6. Standardize categorical casing
    def normalize_text(x):
        if isinstance(x, str):
            return x.strip().title()
        return x

    cat_cols = ["Education", "Residence", "Wealth", "Sex", "DeliveryPlace", "Tetanus", "MultipleBirth"]

    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)

    return df
