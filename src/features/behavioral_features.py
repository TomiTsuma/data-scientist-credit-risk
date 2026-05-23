import pandas as pd


def build_behavioral_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['days_since_last_visit'] = (pd.to_datetime('today') - pd.to_datetime(df['last_visit'])).dt.days
    return df
