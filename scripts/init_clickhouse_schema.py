from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "src" / "sql"

CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", "9000"))
CH_USER = os.getenv("CLICKHOUSE_USER", "clickhouse_user")
CH_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "clickhouse_password")


def wait_for_clickhouse(max_attempts: int = 60, delay: float = 2.0) -> None:
    from clickhouse_driver import Client

    for attempt in range(1, max_attempts + 1):
        try:
            client = Client(
                host=CH_HOST,
                port=CH_PORT,
                user=CH_USER,
                password=CH_PASSWORD,
            )
            client.execute("SELECT 1")
            print(f"ClickHouse ready ({CH_HOST}:{CH_PORT})")
            return
        except Exception as exc:
            print(f"  waiting for ClickHouse ({attempt}/{max_attempts}): {exc}")
            time.sleep(delay)
    raise RuntimeError("ClickHouse did not become ready in time")


def split_sql(text: str) -> list[str]:
    """Split SQL file into executable statements."""
    stripped = re.sub(r"--[^\n]*", "", text)
    parts = [p.strip() for p in stripped.split(";") if p.strip()]
    return parts


def apply_schema() -> None:
    from clickhouse_driver import Client

    client = Client(
        host=CH_HOST,
        port=CH_PORT,
        user=CH_USER,
        password=CH_PASSWORD,
    )

    files = sorted(SQL_DIR.glob("*.sql"))
    for path in files:
        if path.name.startswith(("03_", "04_")):
            print(f"  skip {path.name} (run populate_marts.py after load)")
            continue
        print(f"  apply {path.name}")
        statements = split_sql(path.read_text(encoding="utf-8"))
        for stmt in statements:
            client.execute(stmt)


def main() -> None:
    print("Initializing ClickHouse schema...")
    wait_for_clickhouse()
    apply_schema()
    print("Schema initialization complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
