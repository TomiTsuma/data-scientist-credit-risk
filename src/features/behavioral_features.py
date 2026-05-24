import numpy as np
import pandas as pd


def build_behavioral_features(df: pd.DataFrame) -> pd.DataFrame:
    """Acquisition and operational behavior features."""
    df = df.copy()
    if "days_to_sale" in df.columns:
        df["lead_conversion_speed"] = df["days_to_sale"].fillna(df["days_to_sale"].median())
    else:
        df["lead_conversion_speed"] = np.nan

    if "installation_delay_days" in df.columns:
        df["installation_delay_days"] = df["installation_delay_days"].fillna(
            df["installation_delay_days"].median()
        )
        df["install_delay_flag"] = (df["installation_delay_days"] < 0).astype(int)
    else:
        df["install_delay_flag"] = 0

    if "lead_source" in df.columns:
        df["lead_quality_score"] = df.groupby("lead_source")["is_healthy"].transform("mean").fillna(
            0.5
        )
    else:
        df["lead_quality_score"] = 0.5

    # RFM-style recency proxy: newer accounts + arrears = higher engagement risk
    if "account_age_days" in df.columns:
        max_age = max(df["account_age_days"].max(), 1)
        df["recency_score"] = 1.0 - (df["account_age_days"] / max_age)
        ac = df["account_count"] if "account_count" in df.columns else pd.Series(1, index=df.index)
        df["frequency_score"] = ac.clip(upper=3) / 3.0
        df["monetary_score"] = df["financed_amount"].rank(pct=True)
    return df
