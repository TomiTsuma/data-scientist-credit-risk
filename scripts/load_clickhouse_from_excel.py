from __future__ import annotations
import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "raw"
    / "Senior_Data_Scientist_Assessment_Data (1) (1) (1) (1).xlsx"
)

CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", "9000"))
CH_USER = os.getenv("CLICKHOUSE_USER", "clickhouse_user")
CH_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "clickhouse_password")
DB = os.getenv("CLICKHOUSE_DB", "sunculture_db")


def get_client():
    from clickhouse_driver import Client

    return Client(
        host=CH_HOST,
        port=CH_PORT,
        user=CH_USER,
        password=CH_PASSWORD,
    )


def wait_for_clickhouse(max_attempts: int = 60, delay: float = 2.0) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            get_client().execute("SELECT 1")
            return
        except Exception as exc:
            print(f"  waiting for ClickHouse ({attempt}/{max_attempts}): {exc}")
            time.sleep(delay)
    raise RuntimeError("ClickHouse not ready")


def ch_count(client, table: str) -> int:
    return int(client.execute(f"SELECT count() FROM {DB}.{table}")[0][0])


def bulk_insert(client, table: str, columns: list[str], rows: list[tuple]) -> None:
    if not rows:
        return
    cols = ", ".join(columns)
    client.execute(f"INSERT INTO {DB}.{table} ({cols}) VALUES", rows)


def load_sheets(path: Path) -> dict[str, pd.DataFrame]:
    names = [
        "Customers",
        "Departments",
        "Users",
        "Products",
        "Leads",
        "Installations",
        "Accounts",
        "Sales",
    ]
    return pd.read_excel(path, sheet_name=names, engine="openpyxl")


def load_dimensions(
    client,
    customers: pd.DataFrame,
    departments: pd.DataFrame,
    users: pd.DataFrame,
    products: pd.DataFrame,
    leads: pd.DataFrame,
    accounts: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Populate dimension tables; return in-memory dimension frames for fact joins."""

    # --- dim_country ---
    countries = customers["region"].unique()
    currency_map = {"uganda": "USh", "kenya": "KSh", "civ": "CFA Franc"}
    dim_countries = pd.DataFrame(
        {
            "country_name": countries,
            "currency": [currency_map.get(c, "KES") for c in countries],
        }
    )
    bulk_insert(
        client,
        "dim_country",
        ["country_name", "currency"],
        [(r.country_name, r.currency) for r in dim_countries.itertuples()],
    )
    dim_countries = pd.DataFrame(
        client.execute(f"SELECT country_id, country_name, currency FROM {DB}.dim_country"),
        columns=["country_id", "country_name", "currency"],
    )

    # --- dim_location ---
    country_locations = customers[["region", "Location"]].value_counts().reset_index()
    country_locations = country_locations.rename(columns={"Location": "location_name"})
    dim_location = dim_countries.merge(
        country_locations,
        left_on="country_name",
        right_on="region",
        how="outer",
    )[["country_id", "location_name"]]
    dim_location = dim_location.dropna(subset=["location_name", "country_id"])
    bulk_insert(
        client,
        "dim_location",
        ["location_name", "country_id"],
        [(r.location_name, r.country_id) for r in dim_location.itertuples()],
    )
    dim_location = pd.DataFrame(
        client.execute(
            f"SELECT location_id, country_id, location_name FROM {DB}.dim_location"
        ),
        columns=["location_id", "country_id", "location_name"],
    )

    # --- dim_customer ---
    dim_customers = customers.copy()
    dim_customers["Date_of_birth"] = pd.to_datetime(
        dim_customers["Date_of_birth"], errors="coerce"
    )
    dim_customers["Age"] = dim_customers["Date_of_birth"].apply(
        lambda x: datetime.now().year - x.year if pd.notna(x) else 0
    )
    dim_customers["age_bucket"] = pd.cut(
        dim_customers["Age"],
        bins=[0, 18, 35, 50, 100],
        labels=["0-18", "19-35", "36-50", "51+"],
    ).astype(str)
    dim_customers["created_at"] = pd.to_datetime(
        dim_customers["created_at"], errors="coerce"
    )
    dim_customers = dim_customers.merge(
        dim_countries, left_on="region", right_on="country_name", how="left"
    )
    dim_customers = dim_customers.merge(
        dim_location,
        left_on=["country_id", "Location"],
        right_on=["country_id", "location_name"],
        how="left",
    )
    cust_rows = [
        (
            row["id"],
            row["Gender"],
            row["Date_of_birth"].date() if pd.notna(row["Date_of_birth"]) else None,
            int(row["Age"]),
            row["age_bucket"],
            row["country_id"],
            row["location_id"],
            float(row["Latitude"]) if pd.notna(row["Latitude"]) else 0.0,
            float(row["Longitude"]) if pd.notna(row["Longitude"]) else 0.0,
            row["created_at"],
        )
        for _, row in dim_customers.iterrows()
        if pd.notna(row.get("country_id")) and pd.notna(row.get("location_id"))
    ]
    bulk_insert(
        client,
        "dim_customer",
        [
            "customer_id",
            "gender",
            "date_of_birth",
            "age",
            "age_bucket",
            "country_id",
            "location_id",
            "latitude",
            "longitude",
            "created_at",
        ],
        cust_rows,
    )

    # --- dim_product ---
    dim_product = products.copy()
    dim_product["created_at"] = pd.to_datetime(dim_product["created_at"], errors="coerce")
    dim_product = dim_product.rename(
        columns={"Id": "product_id", "Product": "product_name", "is_refurb": "refurb_status"}
    )
    dim_product["refurb_status"] = dim_product["refurb_status"].map(
        {True: "Refurbished", False: "New"}
    ).fillna("New")
    bulk_insert(
        client,
        "dim_product",
        ["product_id", "product_name", "refurb_status", "created_at"],
        [
            (r.product_id, r.product_name, r.refurb_status, r.created_at)
            for r in dim_product.itertuples()
        ],
    )

    # --- dim_lead_source ---
    lead_sources = leads["Source"].dropna().unique()
    for src in lead_sources:
        client.execute(
            f"INSERT INTO {DB}.dim_lead_source (lead_source_name) VALUES",
            [(src,)],
        )
    dim_lead_source = pd.DataFrame(
        client.execute(
            f"SELECT lead_source_id, lead_source_name FROM {DB}.dim_lead_source"
        ),
        columns=["lead_source_id", "lead_source_name"],
    )

    # --- dim_department / dim_employee ---
    bulk_insert(
        client,
        "dim_department",
        ["department_id", "department_name"],
        [(r.Id, r.name) for r in departments.itertuples()],
    )
    users = users.copy()
    users["created_at"] = pd.to_datetime(users["created_at"], errors="coerce")
    bulk_insert(
        client,
        "dim_employee",
        ["employee_id", "full_name", "department_id", "created_at"],
        [(r.Id, r.Name, r.departmentId, r.created_at) for r in users.itertuples()],
    )

    # --- dim_account_status ---
    statuses = accounts["status"].unique()
    risk = {
        "Arrears": "High Risk",
        "Complete": "Low Risk",
        "Repossession": "High Risk",
        "Repossed": "High Risk",
        "Refunded": "Low Risk",
        "Write Off": "High Risk",
        "No Deposit": "Low Risk",
        "Advance": "Low Risk",
    }
    bulk_insert(
        client,
        "dim_account_status",
        ["account_status_name", "risk_category"],
        [(s, risk.get(s, "Low Risk")) for s in statuses],
    )
    dim_account_status = pd.DataFrame(
        client.execute(
            f"SELECT account_status_id, account_status_name, risk_category FROM {DB}.dim_account_status"
        ),
        columns=["account_status_id", "account_status_name", "risk_category"],
    )

    dim_customer = pd.DataFrame(
        client.execute(
            f"SELECT customer_id, gender, country_id, location_id FROM {DB}.dim_customer"
        ),
        columns=["customer_id", "gender", "country_id", "location_id"],
    )

    return {
        "dim_countries": dim_countries,
        "dim_location": dim_location,
        "dim_customers": dim_customers,
        "dim_lead_source": dim_lead_source,
        "dim_account_status": dim_account_status,
        "dim_customer": dim_customer,
    }


def load_fact_sales(
    client,
    sales: pd.DataFrame,
    accounts: pd.DataFrame,
    leads: pd.DataFrame,
    dims: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    fact_sales = sales.rename(columns={"Id": "sale_id", "Sale_date": "sale_date"})
    fact_accounts = accounts.rename(
        columns={
            "id": "account_id",
            "status": "account_status",
            "type": "account_type",
            "Installation_id": "installation_id",
            "Agent_id": "employee_id",
            "Proudct_id": "product_id",
        }
    )
    fact_sales = fact_sales.merge(
        fact_accounts[
            [
                "account_id",
                "customer_id",
                "account_status",
                "account_type",
                "installation_id",
                "employee_id",
                "product_id",
                "lead_id",
            ]
        ],
        on="account_id",
        how="left",
    )
    fact_sales = fact_sales.merge(
        leads[["Id", "Source"]],
        left_on="lead_id",
        right_on="Id",
        how="left",
    )
    fact_sales = fact_sales.merge(
        dims["dim_lead_source"],
        left_on="Source",
        right_on="lead_source_name",
        how="left",
    )
    fact_sales = fact_sales.merge(
        dims["dim_customers"][["id", "country_id"]],
        left_on="customer_id",
        right_on="id",
        how="left",
    )
    fact_sales["sale_date"] = pd.to_datetime(fact_sales["sale_date"], errors="coerce")
    fact_sales["created_at"] = pd.to_datetime(fact_sales["created_at"], errors="coerce")
    fact_sales["sale_timestamp"] = fact_sales["created_at"]

    rows = []
    for _, row in fact_sales.iterrows():
        if pd.isna(row.get("country_id")) or pd.isna(row.get("lead_source_id")):
            continue
        rows.append(
            (
                str(row["sale_id"]),
                str(row["customer_id"]),
                str(row["product_id"]),
                row["lead_source_id"],
                str(row["employee_id"]),
                str(row["account_id"]),
                row["country_id"],
                row["sale_date"].date() if pd.notna(row["sale_date"]) else None,
                row["sale_timestamp"],
                str(row["account_type"]) if pd.notna(row.get("account_type")) else "",
                str(row["account_status"]) if pd.notna(row.get("account_status")) else "",
                row["created_at"],
            )
        )
    bulk_insert(
        client,
        "fact_sales",
        [
            "sale_id",
            "customer_id",
            "product_id",
            "lead_source_id",
            "agent_id",
            "account_id",
            "country_id",
            "sale_date",
            "sale_timestamp",
            "account_type",
            "account_status",
            "created_at",
        ],
        rows,
    )
    return fact_sales


def load_fact_accounts_snapshots(
    client,
    accounts: pd.DataFrame,
    fact_sales: pd.DataFrame,
    dims: dict[str, pd.DataFrame],
) -> None:
    snap = accounts.copy(deep=True)
    snap = snap.merge(
        dims["dim_customers"].rename(columns={"id": "customer_id"})[
            ["customer_id", "country_id"]
        ],
        on="customer_id",
        how="left",
    )
    snap = snap.merge(
        fact_sales[["lead_id", "lead_source_id"]].drop_duplicates("lead_id"),
        on="lead_id",
        how="left",
    )
    snap = snap.merge(
        dims["dim_account_status"].rename(columns={"account_status_name": "account_status"})[
            ["account_status", "account_status_id"]
        ],
        left_on="status",
        right_on="account_status",
        how="left",
    )
    snap["created_at"] = pd.to_datetime(snap["created_at"], errors="coerce")
    snap["First_installment_date"] = pd.to_datetime(
        snap["First_installment_date"], errors="coerce"
    )

    def enrich(group: pd.DataFrame) -> pd.DataFrame:
        group = group.sort_values("created_at")
        min_date = group["created_at"].min()
        group["account_age_days"] = (group["created_at"] - min_date).dt.days.astype(int)
        group["is_currently_in_arrears"] = group["account_status"].eq("Arrears")
        return group

    snap = snap.groupby("id", group_keys=False).apply(enrich)

    rows = []
    for _, row in snap.iterrows():
        if pd.isna(row.get("country_id")) or pd.isna(row.get("account_status_id")):
            continue
        rows.append(
            (
                str(row["id"]),
                str(row["customer_id"]),
                str(row["Proudct_id"]),
                row["country_id"],
                row["account_status_id"],
                str(row["lead_source_id"]) if pd.notna(row.get("lead_source_id")) else "",
                row["created_at"],
                int(row["account_age_days"]),
                bool(row["is_currently_in_arrears"]),
                str(row["type"]),
                row["First_installment_date"].date()
                if pd.notna(row["First_installment_date"])
                else None,
            )
        )
    bulk_insert(
        client,
        "fact_accounts_snapshots",
        [
            "account_id",
            "customer_id",
            "product_id",
            "country_id",
            "account_status_id",
            "lead_source_id",
            "created_at",
            "account_age_days",
            "is_currently_in_arrears",
            "payment_type",
            "activation_date",
        ],
        rows,
    )


def load_fact_installations(
    client,
    installations: pd.DataFrame,
    accounts: pd.DataFrame,
    fact_sales: pd.DataFrame,
    dims: dict[str, pd.DataFrame],
) -> None:
    inst = installations.rename(columns={"Id": "installation_id"})
    acc = accounts.rename(
        columns={
            "id": "account_id",
            "Installation_id": "installation_id",
            "status": "installation_status",
            "Proudct_id": "product_id",
        }
    )[["account_id", "installation_id", "customer_id", "installation_status", "product_id"]]
    inst = inst.merge(acc, on="installation_id", how="left")
    inst = inst.merge(
        dims["dim_customer"][["customer_id", "country_id", "location_id"]],
        on="customer_id",
        how="left",
    )
    inst = inst.merge(
        fact_sales[["account_id", "sale_date"]], on="account_id", how="left"
    )
    inst["Installation_date"] = pd.to_datetime(inst["Installation_date"], errors="coerce")
    inst["sale_date"] = pd.to_datetime(inst["sale_date"], errors="coerce")
    inst["created_at"] = pd.to_datetime(inst["created_at"], errors="coerce")

    rows = []
    for _, row in inst.iterrows():
        if pd.isna(row.get("country_id")):
            continue
        rows.append(
            (
                str(row["installation_id"]),
                str(row["customer_id"]),
                str(row["account_id"]),
                str(row["product_id"]),
                str(row["engineer_id"]),
                row["country_id"],
                row["location_id"] if pd.notna(row.get("location_id")) else row["country_id"],
                row["sale_date"].date() if pd.notna(row["sale_date"]) else None,
                row["Installation_date"].date()
                if pd.notna(row["Installation_date"])
                else None,
                str(row["installation_status"]),
                row["created_at"],
            )
        )
    bulk_insert(
        client,
        "fact_installations",
        [
            "installation_id",
            "customer_id",
            "account_id",
            "product_id",
            "engineer_id",
            "country_id",
            "location_id",
            "sale_date",
            "installation_date",
            "installation_status",
            "created_at",
        ],
        rows,
    )


def load_fact_lead_funnel(
    client,
    leads: pd.DataFrame,
    accounts: pd.DataFrame,
    sales: pd.DataFrame,
    dims: dict[str, pd.DataFrame],
) -> None:
    funnel = leads.rename(columns={"Id": "lead_id", "Source": "lead_source_name"})
    funnel = funnel.merge(dims["dim_lead_source"], on="lead_source_name", how="left")
    account_sales = accounts.rename(
        columns={
            "id": "account_id",
            "created_at": "account_created_at",
            "Dispatch_date": "dispatch_date",
            "Agent_id": "agent_id",
        }
    )[
        ["account_id", "lead_id", "Installation_id", "account_created_at", "dispatch_date", "agent_id"]
    ].merge(
        sales.rename(columns={"Sale_date": "sale_date", "Id": "sale_id"})[
            ["sale_id", "sale_date", "account_id"]
        ],
        on="account_id",
        how="left",
    )
    funnel = funnel.merge(account_sales, on="lead_id", how="left")

    funnel["created_at"] = pd.to_datetime(funnel["created_at"], errors="coerce")
    funnel["account_created_at"] = pd.to_datetime(
        funnel["account_created_at"], errors="coerce"
    )
    funnel["sale_date"] = pd.to_datetime(funnel["sale_date"], errors="coerce")
    funnel["dispatch_date"] = pd.to_datetime(funnel["dispatch_date"], errors="coerce")

    funnel["converted_to_account"] = funnel["lead_id"].isin(accounts["lead_id"]).astype(int)
    funnel["converted_to_sale"] = funnel["sale_id"].notna().astype(int)
    funnel["converted_to_installation"] = funnel["Installation_id"].notna().astype(int)

    funnel["days_to_account"] = (
        funnel["account_created_at"] - funnel["created_at"]
    ).dt.days
    funnel["days_to_sale"] = (funnel["sale_date"] - funnel["created_at"]).dt.days
    funnel["days_to_dispatch"] = (funnel["dispatch_date"] - funnel["created_at"]).dt.days

    for col in ["days_to_account", "days_to_sale", "days_to_dispatch"]:
        funnel[col] = funnel[col].fillna(-1).astype(int)
        funnel[col] = funnel[col].apply(lambda x: x if x >= 0 else 99999)
        funnel[col] = funnel[col].replace(99999, None)

    funnel["lead_quality_score"] = (
        funnel["converted_to_account"] * 0.4
        + funnel["converted_to_sale"] * 0.3
        + funnel["converted_to_installation"] * 0.3
    ).astype("float32")

    records = []
    for _, row in funnel.iterrows():
        try:
            ls_id = row["lead_source_id"]
            if pd.isna(ls_id):
                continue
            uuid_val = str(UUID(str(ls_id)))
        except (ValueError, AttributeError):
            continue
        records.append(
            (
                str(row["lead_id"]),
                str(row["customer_id"]) if pd.notna(row["customer_id"]) else "",
                uuid_val,
                str(row["agent_id"]) if pd.notna(row.get("agent_id")) else None,
                row["created_at"].date() if pd.notna(row["created_at"]) else None,
                int(row["converted_to_account"]),
                int(row["converted_to_sale"]),
                int(row["converted_to_installation"]),
                row["days_to_account"],
                row["days_to_sale"],
                row["days_to_dispatch"],
                float(row["lead_quality_score"]),
            )
        )

    if records:
        client.execute(
            f"""
            INSERT INTO {DB}.fact_lead_funnel
            (lead_id, customer_id, lead_source_id, agent_id, lead_created_date,
             converted_to_account, converted_to_sale, converted_to_installation,
             days_to_account, days_to_sale, days_to_dispatch, lead_quality_score)
            VALUES
            """,
            records,
        )


def build_parquet_for_ai() -> None:
    """Materialize customer_features_base.parquet for the AI platform."""
    from src.data.joins import build_customer_analytics_table, save_customer_base

    df = build_customer_analytics_table()
    save_customer_base(df)
    print(f"  wrote {len(df)} rows to data/processed/customer_features_base.parquet")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load Excel assessment data into ClickHouse")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--skip-if-loaded",
        action="store_true",
        help="Skip load when dim_customer already has rows",
    )
    args = parser.parse_args()

    if not args.source.exists():
        print(f"ERROR: workbook not found: {args.source}", file=sys.stderr)
        sys.exit(1)

    sys.path.insert(0, str(ROOT))
    wait_for_clickhouse()
    client = get_client()

    if args.skip_if_loaded and ch_count(client, "dim_customer") > 0:
        print("Data already loaded (dim_customer non-empty); skipping.")
        return

    print(f"Loading workbook: {args.source}")
    sheets = load_sheets(args.source)

    print("[1/6] Dimensions...")
    dims = load_dimensions(
        client,
        sheets["Customers"],
        sheets["Departments"],
        sheets["Users"],
        sheets["Products"],
        sheets["Leads"],
        sheets["Accounts"],
    )

    print("[2/6] fact_sales...")
    fact_sales = load_fact_sales(
        client,
        sheets["Sales"],
        sheets["Accounts"],
        sheets["Leads"],
        dims,
    )

    print("[3/6] fact_accounts_snapshots...")
    load_fact_accounts_snapshots(client, sheets["Accounts"], fact_sales, dims)

    print("[4/6] fact_installations...")
    load_fact_installations(
        client,
        sheets["Installations"],
        sheets["Accounts"],
        fact_sales,
        dims,
    )

    print("[5/6] fact_lead_funnel...")
    load_fact_lead_funnel(
        client,
        sheets["Leads"],
        sheets["Accounts"],
        sheets["Sales"],
        dims,
    )

    print("[6/6] Analytical marts + AI parquet...")
    from scripts.populate_marts import populate_marts

    populate_marts(client)
    build_parquet_for_ai()

    print("Load complete.")
    for table in [
        "dim_customer",
        "fact_sales",
        "fact_accounts_snapshots",
        "fact_installations",
        "fact_lead_funnel",
        "mart_customer_account_analytics",
    ]:
        print(f"  {table}: {ch_count(client, table)} rows")


if __name__ == "__main__":
    main()
