import pandas as pd
from pathlib import Path


def load_raw_data(path: Path) -> pd.DataFrame:
    return pd.read_excel(path)


def load_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)
