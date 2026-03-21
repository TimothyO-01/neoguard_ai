import pandas as pd
import numpy as np

def preprocess_input(df):
    # Fill numeric features with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    # Encode categorical variables if necessary
    for col in df.select_dtypes(include=["object"]):
        df[col] = pd.factorize(df[col])[0]

    return dfimport pandas as pd
import numpy as np

def preprocess_input(df):
    # Fill numeric features with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    # Encode categorical variables if necessary
    for col in df.select_dtypes(include=["object"]):
        df[col] = pd.factorize(df[col])[0]

    return df
