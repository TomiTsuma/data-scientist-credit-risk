"""Build customer-level analytical tables from assessment sources."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.loaders import load_all_sheets, resolve_excel_path
from src.features.behavioral_features import build_behavioral_features
from src.features.customer_features import create_customer_features
from src.features.risk_features import create_risk_features

# Account statuses treated as distressed / default-like for modeling
ARREARS_STATUSES = {"Arrears", "No Deposit"}
DEFAULT_STATUSES = {"Write Off", "Repossession", "Repossed"}
HEALTHY_STATUSES = {"Complete", "Advance"}


def _normalize_country(region: str) -> str:
    if pd.isna(region):
        return "Unknown"
    r = str(region).strip().lower()
    mapping = {"kenya": "Kenya", "uganda": "Uganda", "civ": "Côte d'Ivoire"}
    return mapping.get(r, r.title())


def _account_age_days(created_at: pd.Series, reference: pd.Timestamp | None = None) -> pd.Series:
    ref = reference or pd.Timestamp.now().normalize()
    created = pd.to_datetime(created_at, errors="coerce")
    return (ref - created).dt.days.clip(lower=0)


def build_account_level_table(sheets: dict[str, pd.DataFrame] | None = None) -> pd.DataFrame:
    """Join accounts to customers, products, sales, installations, leads."""
    if sheets is None:
        sheets = load_all_sheets()

    customers = sheets["Customers"].rename(
        columns={
            "id": "customer_id",
            "Gender": "gender",
            "Location": "location",
            "Date_of_birth": "date_of_birth",
            "region": "region",
        }
    )
    accounts = sheets["Accounts"].rename(
        columns={
            "id": "account_id",
            "status": "account_status",
            "type": "payment_type",
            "Installation_id": "installation_id",
            "Proudct_id": "product_id",
            "Agent_id": "agent_id",
        }
    )
    products = sheets["Products"].rename(
        columns={"Id": "product_id", "Product": "product_name", "is_refurb": "is_refurb"}
    )
    sales = sheets["Sales"].rename(columns={"Id": "sale_id", "Sale_date": "sale_date"})
    installations = sheets["Installations"].rename(
        columns={"Id": "installation_id", "Installation_date": "installation_date"}
    )
    leads = sheets["Leads"].rename(columns={"Id": "lead_id", "Source": "lead_source"})

    accounts = accounts.rename(columns={"created_at": "account_created_at"})
    customers = customers.rename(columns={"created_at": "customer_created_at"})

    customers["country_name"] = customers["region"].map(_normalize_country)
    customers["date_of_birth"] = pd.to_datetime(customers["date_of_birth"], errors="coerce")
    ref_date = pd.to_datetime(accounts["account_created_at"], errors="coerce").max()
    customers["age"] = (
        (ref_date - customers["date_of_birth"]).dt.days / 365.25
    ).clip(18, 90)
    customers["age"] = customers["age"].round().astype(int)

    def age_bucket(age: float) -> str:
        if pd.isna(age):
            return "Unknown"
        if age < 25:
            return "<25"
        if age < 35:
            return "25-34"
        if age < 50:
            return "35-49"
        return "50+"

    customers["age_bucket"] = customers["age"].astype(float).map(age_bucket)

    df = accounts.merge(customers, on="customer_id", how="left")
    df = df.merge(
        products[["product_id", "product_name", "is_refurb"]],
        on="product_id",
        how="left",
    )
    df = df.merge(sales[["account_id", "sale_id", "sale_date"]], on="account_id", how="left")
    df = df.merge(
        installations[["installation_id", "installation_date", "engineer_id"]],
        on="installation_id",
        how="left",
    )
    df = df.merge(
        leads[["lead_id", "lead_source", "customer_id"]].drop_duplicates("lead_id"),
        on=["lead_id", "customer_id"],
        how="left",
    )

    df["product_tier"] = np.where(df["is_refurb"].fillna(False), "Refurbished", "New")
    df["product_category"] = df["product_name"]
    df["account_age_days"] = _account_age_days(df["account_created_at"], ref_date)
    df["is_in_arrears"] = df["account_status"].isin(ARREARS_STATUSES).astype(int)
    df["is_default"] = df["account_status"].isin(DEFAULT_STATUSES).astype(int)
    df["is_healthy"] = df["account_status"].isin(HEALTHY_STATUSES).astype(int)

    sale_dt = pd.to_datetime(df["sale_date"], errors="coerce")
    install_dt = pd.to_datetime(df["installation_date"], errors="coerce")
    df["installation_delay_days"] = (install_dt - sale_dt).dt.days

    if "created_at" in leads.columns:
        lead_created = leads.set_index("lead_id")["created_at"]
        lead_dt = pd.to_datetime(df["lead_id"].map(lead_created), errors="coerce")
        df["days_to_sale"] = (sale_dt - lead_dt).dt.days.clip(lower=0)
    else:
        df["days_to_sale"] = np.nan

    # Financial proxies (no balances in source data)
    tier_value = {"New": 3, "Refurbished": 1}
    df["product_tier_ord"] = df["product_tier"].map(tier_value).fillna(2)
    df["financed_amount"] = np.where(
        df["payment_type"] == "PAYG",
        df["product_tier_ord"] * 50000,
        df["product_tier_ord"] * 80000,
    )
    df["outstanding_balance"] = np.where(
        df["is_healthy"] == 1,
        df["financed_amount"] * 0.2,
        np.where(df["is_default"] == 1, df["financed_amount"] * 0.9, df["financed_amount"] * 0.55),
    )
    df["arrears_balance"] = np.where(df["is_in_arrears"] == 1, df["outstanding_balance"] * 0.4, 0.0)
    df["days_past_due"] = np.where(
        df["is_in_arrears"] == 1,
        np.clip(df["account_age_days"] * 0.15, 7, 90),
        np.where(df["is_default"] == 1, 90, 0),
    ).astype(int)
    df["repayment_progress"] = np.clip(
        1.0 - (df["outstanding_balance"] / df["financed_amount"].replace(0, np.nan)),
        0,
        1,
    ).fillna(0.5)

    return df


def aggregate_to_customer(account_df: pd.DataFrame) -> pd.DataFrame:
    """One row per customer (accounts are 1:1 in this dataset)."""
    if account_df["customer_id"].duplicated().any():
        def weighted_repayment(g: pd.DataFrame) -> float:
            w = g["outstanding_balance"].replace(0, 1)
            return float(np.average(g["repayment_progress"], weights=w))

        agg = account_df.groupby("customer_id").agg(
            country_name=("country_name", "first"),
            gender=("gender", "first"),
            age=("age", "first"),
            age_bucket=("age_bucket", "first"),
            location=("location", "first"),
            account_count=("account_id", "count"),
            financed_amount=("financed_amount", "sum"),
            outstanding_balance=("outstanding_balance", "sum"),
            arrears_balance=("arrears_balance", "sum"),
            days_past_due=("days_past_due", "max"),
            is_in_arrears=("is_in_arrears", "max"),
            is_default=("is_default", "max"),
            is_healthy=("is_healthy", "max"),
            account_age_days=("account_age_days", "max"),
            payment_type=("payment_type", lambda s: s.mode().iloc[0] if len(s) else "PAYG"),
            product_tier=("product_tier", lambda s: s.mode().iloc[0] if len(s) else "New"),
            product_category=("product_category", lambda s: s.mode().iloc[0] if len(s) else ""),
            account_status=("account_status", "first"),
            lead_source=("lead_source", "first"),
            installation_delay_days=("installation_delay_days", "median"),
            days_to_sale=("days_to_sale", "median"),
        )
        agg["repayment_progress"] = account_df.groupby("customer_id", group_keys=False).apply(
            weighted_repayment
        )
        return agg.reset_index()

    return account_df.copy()


def build_customer_analytics_table(sheets: dict[str, pd.DataFrame] | None = None) -> pd.DataFrame:
    """Customer-level table ready for feature engineering."""
    account_df = build_account_level_table(sheets)
    customer_df = aggregate_to_customer(account_df)
    customer_df = create_customer_features(customer_df)
    customer_df = create_risk_features(customer_df)
    customer_df = build_behavioral_features(customer_df)
    return customer_df


def save_customer_base(df: pd.DataFrame, path=None) -> None:
    from src.config.config import Config

    path = path or Config().processed_dir / "customer_features_base.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
