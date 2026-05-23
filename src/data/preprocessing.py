import pandas as pd


def clean_customer_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df


def impute_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    return df.fillna({'age': df['age'].median() if 'age' in df else 0})
