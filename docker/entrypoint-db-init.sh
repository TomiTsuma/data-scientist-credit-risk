#!/bin/sh
set -e
python scripts/init_clickhouse_schema.py
python scripts/load_clickhouse_from_excel.py --skip-if-loaded
