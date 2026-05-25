---
name: credit-collections
description: SMART collections and credit mitigation recommendations from assessment data only.
---

# Credit Collections

Each recommendation must include:

- **Filter** (SQL-like or tool filters)
- **Baseline** (%, n from tools)
- **Action** (operations/marketing/credit)
- **Target** (measurable within a quarter)
- **Measure** (metric to track weekly/monthly)

Use `query_customers` and `get_portfolio_kpis` to quantify baselines. Cross-check `credit_risk_recommendations` report for alignment.

Never recommend actions that require external bureau or MoMo data without labeling them as future-state.
