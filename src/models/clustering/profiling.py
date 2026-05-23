import pandas as pd


def profile_cluster_segments(df: pd.DataFrame, label_column: str) -> pd.DataFrame:
    return df.groupby(label_column).agg(['mean', 'median', 'count'])
