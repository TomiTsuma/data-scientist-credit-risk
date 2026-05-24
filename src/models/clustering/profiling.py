"""Business profiling of cluster segments."""

from __future__ import annotations

import pandas as pd

PROFILE_METRICS = [
    "age",
    "account_age_days",
    "financed_amount",
    "outstanding_balance",
    "repayment_progress",
    "arrears_rate",
    "days_past_due",
    "is_in_arrears",
    "is_default",
    "risk_stress_score",
    "lead_conversion_speed",
    "installation_delay_days",
]


def profile_cluster_segments(df: pd.DataFrame, label_column: str = "segment_id") -> pd.DataFrame:
    """Aggregate numeric metrics by segment."""
    metrics = [c for c in PROFILE_METRICS if c in df.columns]
    agg = df.groupby(label_column)[metrics].agg(["mean", "median", "count"])
    agg.columns = ["_".join(col).strip() for col in agg.columns]
    sizes = df.groupby(label_column).size().rename("customer_count")
    agg = agg.join(sizes)
    agg["pct_of_customers"] = (agg["customer_count"] / len(df) * 100).round(1)
    return agg.reset_index()


def segment_lifts(df: pd.DataFrame, label_column: str = "segment_id") -> pd.DataFrame:
    """Mean lift vs portfolio for key metrics."""
    metrics = [c for c in PROFILE_METRICS if c in df.columns]
    global_mean = df[metrics].mean()
    rows = []
    for seg, g in df.groupby(label_column):
        row = {"segment_id": seg, "size": len(g)}
        for m in metrics:
            row[f"{m}_mean"] = g[m].mean()
            row[f"{m}_lift"] = (g[m].mean() / global_mean[m] - 1) if global_mean[m] else 0
        rows.append(row)
    return pd.DataFrame(rows)


def assign_segment_names(lifts: pd.DataFrame) -> dict[int, str]:
    """Heuristic business names from segment lift table."""
    names: dict[int, str] = {}
    fin_median = lifts["financed_amount_mean"].median() if "financed_amount_mean" in lifts.columns else 0
    for _, row in lifts.iterrows():
        seg = int(row["segment_id"])
        arrears = float(row.get("is_in_arrears_mean", 0))
        default = float(row.get("is_default_mean", 0))
        progress = float(row.get("repayment_progress_mean", 0.5))
        financed = float(row.get("financed_amount_mean", 0))
        if default > 0.35:
            names[seg] = "Distressed Defaulters"
        elif arrears > 0.4:
            names[seg] = "Arrears-Stressed PAYG"
        elif progress > 0.65 and financed >= fin_median:
            names[seg] = "Stable Premium Growers"
        elif progress > 0.55:
            names[seg] = "Reliable Mid-Tier"
        else:
            names[seg] = "Early-Tenure Builders"
    return names
