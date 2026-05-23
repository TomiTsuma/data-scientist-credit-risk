import pandas as pd


def create_customer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['customer_age_group'] = pd.cut(df['age'], bins=[0, 25, 40, 60, 100], labels=['<25', '25-40', '40-60', '60+'])
    return df
