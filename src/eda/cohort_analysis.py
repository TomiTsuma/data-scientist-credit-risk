import pandas as pd


def generate_cohort_table(df: pd.DataFrame, cohort_column: str, date_column: str) -> pd.DataFrame:
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])
    df['cohort_month'] = df[date_column].dt.to_period('M')
    return df.groupby(['cohort_month', cohort_column]).size().reset_index(name='count')
