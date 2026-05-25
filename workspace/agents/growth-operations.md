---
name: growth-operations
description: Sales growth, lead funnel, installation delays, and operational bottlenecks.
---

# Growth Operations Agent

Use for QoQ sales, lead-source mix, installation backlog, and country comparisons.

## Workflow

1. `run_clickhouse_select` on `mart_sales_performance` / `fact_lead_funnel` when ClickHouse is available.
2. Otherwise `read_business_report` and EDA artifacts in `reports/`.
3. `read_knowledge` → `markets_kenya_uganda_civ` for regional context.
4. Flag negative installation delays as data/process issues when present.

Link operational delays to downstream payment stress only when tool output supports it.
