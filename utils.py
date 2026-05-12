import pandas as pd
import numpy as np

# -------------------------------
# Data Quality Checks
# -------------------------------
def check_missing(df):
    return df.isnull().sum()

def check_duplicates(df):
    return df.duplicated().sum()

def check_dtypes(df):
    return df.dtypes

# -------------------------------
# Z-Score Anomaly Detection
# -------------------------------
def z_score_outliers(df, column):
    mean = df[column].mean()
    std = df[column].std()

    df['z_score'] = (df[column] - mean) / std
    return df[df['z_score'].abs() > 3]

# -------------------------------
# IQR Method
# -------------------------------
def iqr_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    return df[(df[column] < lower) | (df[column] > upper)]