import numpy as np
import pandas as pd


def create_risk_features(df: pd.DataFrame) -> pd.DataFrame:
    """Payment stress and leverage proxies for segmentation and credit analysis."""
    df = df.copy()
    financed = df["financed_amount"].replace(0, np.nan)
    outstanding = df["outstanding_balance"].replace(0, np.nan)

    df["outstanding_to_financed"] = (outstanding / financed).clip(0, 2).fillna(0)
    df["arrears_rate"] = (df["arrears_balance"] / outstanding).clip(0, 1).fillna(0)
    df["days_past_due_cap"] = df["days_past_due"].clip(0, 90)
    df["risk_stress_score"] = (
        0.4 * df["is_in_arrears"]
        + 0.4 * df["is_default"]
        + 0.2 * (df["days_past_due_cap"] / 90.0)
    )
    if "annual_income" in df.columns and "total_debt" in df.columns:
        df["debt_to_income"] = df["total_debt"] / df["annual_income"].replace(0, 1)
    return df
