import pandas as pd


def create_segmentation_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['recency_score'] = df['recency'].rank(pct=True)
    df['frequency_score'] = df['frequency'].rank(pct=True)
    return df
