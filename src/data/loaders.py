"""Load assessment data from Excel or ClickHouse."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.config.config import Config

CONFIG = Config()


def resolve_excel_path() -> Path:
    """Return the first available assessment workbook."""
    candidates = [
        CONFIG.raw_data_file,
        *sorted(CONFIG.raw_data_dir.glob("Senior_Data_Scientist_Assessment_Data*.xlsx")),
    ]
    for path in candidates:
        if path.exists() and path.name != "Senior_Data_Scientist_Assessment_Data.xlsx":
            # Prefer full multi-sheet workbook over placeholder single-sheet file
            xl = pd.ExcelFile(path)
            if len(xl.sheet_names) > 1:
                return path
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        f"No assessment workbook found under {CONFIG.raw_data_dir}. "
        "Expected Senior_Data_Scientist_Assessment_Data*.xlsx"
    )


def load_raw_data(path: Path | None = None) -> pd.DataFrame:
    """Load placeholder single-sheet data (legacy helper)."""
    path = path or resolve_excel_path()
    return pd.read_excel(path)


def load_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def load_all_sheets(path: Path | None = None) -> dict[str, pd.DataFrame]:
    """Load all assessment Excel sheets into a dict."""
    path = path or resolve_excel_path()
    xl = pd.ExcelFile(path)
    return {name: pd.read_excel(path, sheet_name=name) for name in xl.sheet_names}


def load_from_clickhouse() -> pd.DataFrame | None:
    """Load mart_customer_account_analytics when ClickHouse is available."""
    try:
        from clickhouse_driver import Client
    except ImportError:
        return None

    try:
        client = Client(
            host="localhost",
            port=9000,
            user="clickhouse_user",
            password="clickhouse_password",
        )
        rows, meta = client.execute(
            "SELECT * FROM sunculture_db.mart_customer_account_analytics",
            with_column_types=True,
        )
        columns = [col[0] for col in meta]
        return pd.DataFrame(rows, columns=columns)
    except Exception:
        return None


def load_customer_mart(prefer_clickhouse: bool = False) -> pd.DataFrame:
    """Load customer-level analytics, preferring Excel joins for richer fields."""
    if prefer_clickhouse:
        ch_df = load_from_clickhouse()
        if ch_df is not None and len(ch_df) > 0:
            return ch_df
    from src.data.joins import build_customer_analytics_table

    return build_customer_analytics_table()
