import pandas as pd


def create_risk_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['debt_to_income'] = df['total_debt'] / df['annual_income'].replace(0, 1)
    return df
