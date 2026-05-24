# Credit Risk Mitigation Recommendations

Actionable recommendations derived from the assessment dataset (account-level, customer grain).

## R1: Early intervention for PAYG accounts in arrears

**Filter:** `payment_type = 'PAYG' AND is_in_arrears = 1`

**Baseline:** 24.4% of PAYG customers in arrears (n=2,335); portfolio average 24.1%

**Action:** Trigger automated SMS at first arrears flag and agent callback within 48 hours; offer short-term rescheduling before 30 DPD.

**Target:** Reduce PAYG roll-forward to 30+ DPD by 15% within two collection cycles

**Measure:** Weekly arrears rate and average days_past_due by payment_type

## R2: Tighten underwriting for New product tier

**Filter:** `product_tier = 'New' AND country_name IN (Kenya, Uganda, Côte d'Ivoire)`

**Baseline:** New arrears rate 24.9% vs Refurbished 22.2% (+2.7 pp, n=3,291)

**Action:** Add tier-specific deposit rules and agent training; pause outbound campaigns for high-arrears tier until conversion quality improves.

**Target:** Cut New arrears rate by 3 percentage points in 6 months

**Measure:** Monthly arrears_rate by product_tier and country

## R3: Reallocate acquisition spend away from high-arrears lead sources

**Filter:** `lead_source = 'Partners' (review weekly top-3 sources)`

**Baseline:** 'Partners' arrears 28.2% vs 'Refer and Earn' 21.0% (n=585 vs 632)

**Action:** Cap spend on bottom-quartile lead sources; require pay-per-performance for partners above portfolio arrears rate.

**Target:** Lower portfolio arrears rate by 2 pp within one quarter

**Measure:** Arrears rate by lead_source and CAC proxy (sales per source)
