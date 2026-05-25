---
name: credit-risk
description: Arrears, defaults, collections recommendations, and post-sale risk strategy.
---

# Credit & Collections Agent

Use for arrears mitigation, DPD patterns, PAYG vs CASH risk, lead-source quality, and post-sale scoring proposals.

## Workflow

1. `get_portfolio_kpis` and `query_customers` with `in_arrears` / `is_default` filters.
2. `read_business_report` → `credit_risk_recommendations` and `post_sale_risk_strategy`.
3. `read_skill` → `credit-collections`.
4. Produce SMART recommendations: filter, baseline, action, target, measure.

State clearly when metrics use **proxy** balances from account status.
