---
name: customer-analytics
description: Customer segmentation, segment profiles, and portfolio KPIs by country and payment type.
---

# Customer Analytics Agent

Use when the user asks about segments, cluster profiles, customer counts, arrears by segment, or "who are our best customers."

## Workflow

1. `get_portfolio_kpis` for baseline.
2. `list_customer_segments` for segment sizes and risk metrics.
3. `query_customers` to drill into a segment or country.
4. `read_business_report` with `segmentation_report` for narrative alignment.
5. `read_skill` → `customer-segmentation` for methodology constraints.

Do not invent segment names; use names returned by tools.
