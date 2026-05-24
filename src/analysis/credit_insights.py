"""Actionable credit & collections insights from assessment data."""

from __future__ import annotations

import pandas as pd


def compute_collection_insights(df: pd.DataFrame) -> list[dict]:
    """Return SMART recommendations grounded in portfolio statistics."""
    insights: list[dict] = []

    # 1. PAYG arrears early intervention
    payg = df[df["payment_type"] == "PAYG"]
    payg_arrears = payg["is_in_arrears"].mean() * 100
    overall_arrears = df["is_in_arrears"].mean() * 100
    if len(payg) > 0:
        insights.append(
            {
                "id": "R1",
                "title": "Early intervention for PAYG accounts in arrears",
                "filter": "payment_type = 'PAYG' AND is_in_arrears = 1",
                "baseline": f"{payg_arrears:.1f}% of PAYG customers in arrears (n={len(payg):,}); portfolio average {overall_arrears:.1f}%",
                "action": (
                    "Trigger automated SMS at first arrears flag and agent callback within 48 hours; "
                    "offer short-term rescheduling before 30 DPD."
                ),
                "target": "Reduce PAYG roll-forward to 30+ DPD by 15% within two collection cycles",
                "measure": "Weekly arrears rate and average days_past_due by payment_type",
            }
        )

    # 2. Refurbished product tier risk
    if "product_tier" in df.columns:
        tier = (
            df.groupby("product_tier")
            .agg(arrears_rate=("is_in_arrears", "mean"), n=("customer_id", "count"))
            .reset_index()
        )
        if len(tier) >= 2:
            worst = tier.loc[tier["arrears_rate"].idxmax()]
            best = tier.loc[tier["arrears_rate"].idxmin()]
            lift = (worst["arrears_rate"] - best["arrears_rate"]) * 100
            insights.append(
                {
                    "id": "R2",
                    "title": f"Tighten underwriting for {worst['product_tier']} product tier",
                    "filter": f"product_tier = '{worst['product_tier']}' AND country_name IN (Kenya, Uganda, Côte d'Ivoire)",
                    "baseline": (
                        f"{worst['product_tier']} arrears rate {worst['arrears_rate']*100:.1f}% "
                        f"vs {best['product_tier']} {best['arrears_rate']*100:.1f}% "
                        f"(+{lift:.1f} pp, n={int(worst['n']):,})"
                    ),
                    "action": (
                        "Add tier-specific deposit rules and agent training; pause outbound campaigns "
                        "for high-arrears tier until conversion quality improves."
                    ),
                    "target": f"Cut {worst['product_tier']} arrears rate by 3 percentage points in 6 months",
                    "measure": "Monthly arrears_rate by product_tier and country",
                }
            )

    # 3. Lead source quality
    if "lead_source" in df.columns:
        src = (
            df.groupby("lead_source")
            .agg(
                arrears_rate=("is_in_arrears", "mean"),
                default_rate=("is_default", "mean"),
                n=("customer_id", "count"),
            )
            .query("n >= 30")
            .sort_values("arrears_rate", ascending=False)
        )
        if len(src) > 0:
            bad = src.iloc[0]
            good = src.iloc[-1]
            insights.append(
                {
                    "id": "R3",
                    "title": "Reallocate acquisition spend away from high-arrears lead sources",
                    "filter": f"lead_source = '{bad.name}' (review weekly top-3 sources)",
                    "baseline": (
                        f"'{bad.name}' arrears {bad['arrears_rate']*100:.1f}% vs "
                        f"'{good.name}' {good['arrears_rate']*100:.1f}% "
                        f"(n={int(bad['n'])} vs {int(good['n'])})"
                    ),
                    "action": (
                        "Cap spend on bottom-quartile lead sources; require pay-per-performance "
                        "for partners above portfolio arrears rate."
                    ),
                    "target": "Lower portfolio arrears rate by 2 pp within one quarter",
                    "measure": "Arrears rate by lead_source and CAC proxy (sales per source)",
                }
            )

    # 4. Installation delay anomaly
    if "installation_delay_days" in df.columns:
        neg_pct = (df["installation_delay_days"] < 0).mean() * 100
        pos = df[df["installation_delay_days"] >= 0]
        if len(pos) > 0:
            high_delay = pos[pos["installation_delay_days"] > pos["installation_delay_days"].quantile(0.75)]
            hd_arrears = high_delay["is_in_arrears"].mean() * 100
            low_arrears = pos[pos["installation_delay_days"] <= pos["installation_delay_days"].median()][
                "is_in_arrears"
            ].mean() * 100
            insights.append(
                {
                    "id": "R4",
                    "title": "Prioritize fulfillment for customers with long installation delays",
                    "filter": "installation_delay_days > P75 (valid dates only)",
                    "baseline": (
                        f"{neg_pct:.1f}% of records have negative install delay (data/process issue); "
                        f"among valid installs, top-quartile delay arrears {hd_arrears:.1f}% vs "
                        f"median-or-below {low_arrears:.1f}%"
                    ),
                    "action": (
                        "Fix sale/install date alignment; escalate installs exceeding 14 days with "
                        "proactive customer communication before first payment stress."
                    ),
                    "target": "Reduce arrears among >P75 delay cohort by 10% within 90 days",
                    "measure": "Arrears rate by installation_delay quartile",
                }
            )

    return insights[:4]  # return top 4; caller picks 3+
