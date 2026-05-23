import pandas as pd


def analyze_geography(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby('region').size().reset_index(name='count')
