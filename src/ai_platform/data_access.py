"""Load customer analytics for AI tools (parquet first, ClickHouse optional)."""

from __future__ import annotations

import os

import pandas as pd

from src.ai_platform.config import AI_CONFIG

CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", "9000"))
CH_USER = os.getenv("CLICKHOUSE_USER", "clickhouse_user")
CH_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "clickhouse_password")


def load_customer_frame() -> pd.DataFrame:
    """Customer-level features with optional segment labels."""
    base_path = AI_CONFIG.customer_features_path
    if not base_path.exists():
        from src.data.joins import build_customer_analytics_table

        df = build_customer_analytics_table()
    else:
        df = pd.read_parquet(base_path)

    seg_path = AI_CONFIG.customer_segments_path
    if seg_path.exists():
        seg = pd.read_parquet(seg_path)
        cols = [c for c in seg.columns if c not in df.columns or c == "customer_id"]
        df = df.merge(seg[cols], on="customer_id", how="left")
    return df


def try_clickhouse_query(sql: str) -> dict:
    """Run a read-only ClickHouse query if the server is reachable."""
    try:
        from clickhouse_driver import Client
    except ImportError:
        return {"error": "clickhouse-driver not installed"}

    sql_stripped = sql.strip().rstrip(";")
    if not sql_stripped.lower().startswith("select"):
        return {"error": "Only SELECT queries are allowed"}

    try:
        client = Client(
            host=CH_HOST,
            port=CH_PORT,
            user=CH_USER,
            password=CH_PASSWORD,
        )
        rows, meta = client.execute(sql_stripped, with_column_types=True)
        columns = [c[0] for c in meta]
        return {
            "columns": columns,
            "rows": rows[:200],
            "row_count": len(rows),
            "truncated": len(rows) > 200,
        }
    except Exception as exc:
        return {"error": str(exc), "hint": "Use query_customers or get_portfolio_kpis instead"}
