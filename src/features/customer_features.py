import pandas as pd


def create_customer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Demographic and tenure features for segmentation."""
    df = df.copy()
    if "age" in df.columns:
        df["customer_age_group"] = pd.cut(
            df["age"].astype(float),
            bins=[0, 25, 40, 60, 100],
            labels=["<25", "25-40", "40-60", "60+"],
            include_lowest=True,
        )
    if "account_age_days" in df.columns:
        df["tenure_bucket"] = pd.cut(
            df["account_age_days"],
            bins=[-1, 180, 365, 730, 10_000],
            labels=["<6m", "6-12m", "1-2y", "2y+"],
        )
    return df
