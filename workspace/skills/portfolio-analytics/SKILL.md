---
name: portfolio-analytics
description: Portfolio KPIs, customer filters, and ClickHouse queries for SunCulture assessment data.
---

# Portfolio Analytics

1. Start with `get_portfolio_kpis` (optional `country` filter).
2. Use `query_customers` for cohort drill-down; keep `limit` ≤ 50.
3. Use `run_clickhouse_select` for custom aggregates when ClickHouse is up.
4. Cite exact percentages and counts from tool JSON in the answer.

If tools return errors about missing parquet, instruct the user to run `python3.11 scripts/run_part2_pipeline.py`.
