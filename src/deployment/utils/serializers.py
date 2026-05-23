import pandas as pd


def dataframe_to_dict(df: pd.DataFrame):
    return df.to_dict(orient='records')
