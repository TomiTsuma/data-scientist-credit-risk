# Customer Data Dictionary (Assessment Extract)

## Grain

One row per `customer_id` with an active **Accounts** record (≈4,750 customers).

## Key fields

| Field | Meaning |
|-------|---------|
| `country_name` | Kenya, Uganda, Côte d'Ivoire (from Customers.region) |
| `payment_type` | PAYG or CASH |
| `account_status` | Arrears, Complete, Write Off, Repossession, etc. |
| `product_tier` | New vs Refurbished (from Products.is_refurb) |
| `is_in_arrears` | 1 if status in Arrears, No Deposit |
| `is_default` | 1 if Write Off, Repossession, Repossed |
| `financed_amount` | **Proxy** from tier + payment type |
| `repayment_progress` | **Proxy** from status |
| `lead_source` | From Leads.Source |
| `segment_id` / `segment_name` | From Part 2 K-Means pipeline |

## Joins

Accounts ← Customers, Products, Sales, Installations, Leads.

## Refresh

```powershell
python3.11 scripts/run_part2_pipeline.py
```
