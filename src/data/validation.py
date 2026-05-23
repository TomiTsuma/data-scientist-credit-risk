import pandas as pd


def validate_schema(df: pd.DataFrame, required_columns: list[str]) -> bool:
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    return True


def validate_non_null(df: pd.DataFrame, columns: list[str]) -> bool:
    for column in columns:
        if df[column].isnull().any():
            raise ValueError(f'Null values found in {column}')
    return True
