# Assumptions

## Data grain

- **Customer grain:** One row per `customer_id` with an active account (4,750 customers; 250 customers without accounts excluded).
- **Multi-account:** Dataset is 1:1 customer-to-account; aggregation rules documented for future multi-account cases (sum balances, max DPD).

## Financial proxies

The Excel extract does not include financed amount, outstanding balance, or repayment ledger. Proxies are derived from:

- `account_status` → arrears/default/healthy flags
- `payment_type` (PAYG vs CASH) and `product_tier` (New vs Refurbished) → exposure proxies

## Segmentation

- **Algorithm:** K-Means on `RobustScaler` + one-hot encoded features (`random_state=42`).
- **k selection:** Prefer k ∈ [4, 6] when silhouette is within 0.05 of the global best and all clusters ≥ 5% of customers.
- **Income:** No income field; premium loan targeting uses financed proxy, repayment progress, and default rates.

## Geography

- `region` values normalized to Kenya, Uganda, Côte d'Ivoire.

## Dates

- Reference date for account age: max account `created_at` in the extract.
- Negative installation delays retained with `install_delay_flag` for data quality transparency.
