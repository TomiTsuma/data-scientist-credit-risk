"""
populate_fact_lead_funnel.py
============================
ETL script that reads the raw assessment Excel workbook and populates the
`fact_lead_funnel` table in ClickHouse.

Usage
-----
    # From the project root:
    python3.11 scripts/populate_fact_lead_funnel.py

    # Dry-run (transforms only, no DB write):
    python3.11 scripts/populate_fact_lead_funnel.py --dry-run

    # Point at a different Excel file:
    python3.11 scripts/populate_fact_lead_funnel.py --source "path/to/file.xlsx"

Prerequisites
-------------
    pip install clickhouse-connect pandas openpyxl
    (clickhouse-connect is not in requirements.txt — add it, or install ad hoc)

ClickHouse connection
---------------------
    Set environment variables (or edit the defaults below):
        CLICKHOUSE_HOST      default: localhost
        CLICKHOUSE_PORT      default: 8123
        CLICKHOUSE_USER      default: clickhouse_user
        CLICKHOUSE_PASSWORD  default: clickhouse_password
        CLICKHOUSE_DB        default: sunculture_db
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "Senior_Data_Scientist_Assessment_Data (1) (1) (1) (1).xlsx"
)

# ---------------------------------------------------------------------------
# ClickHouse connection defaults (override via env vars)
# ---------------------------------------------------------------------------
CH_HOST     = os.getenv("CLICKHOUSE_HOST",     "localhost")
CH_PORT     = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CH_USER     = os.getenv("CLICKHOUSE_USER",     "clickhouse_user")
CH_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "clickhouse_password")
CH_DB       = os.getenv("CLICKHOUSE_DB",       "sunculture_db")

TARGET_TABLE = "fact_lead_funnel"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# Surrogate key maps for dimensions not yet loaded from DB.
# If dim tables are already populated, these can be replaced with a live
# SELECT from dim_lead_source / dim_country.
LEAD_SOURCE_MAP: dict[str, int] = {
    "Roadshow":      1,
    "Refer and Earn": 2,
    "Facebook":      3,
    "Website":       4,
    "Walk-in":       5,
    "Telesales":     6,
    "Door to Door":  7,
    "Partners":      8,
}

COUNTRY_MAP: dict[str, int] = {
    "kenya":   1,
    "uganda":  2,
    "civ":     3,
}

# Quality-score weights
WEIGHT_ACCOUNT      = 0.40
WEIGHT_SALE         = 0.30
WEIGHT_INSTALLATION = 0.20
WEIGHT_SPEED        = 0.10
SPEED_DECAY_DAYS    = 90   # days at which speed bonus reaches zero


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(value) -> "pd.Timestamp | pd.NaT":
    """Coerce a cell value to a pandas Timestamp (NaT on failure)."""
    if pd.isna(value):
        return pd.NaT
    if isinstance(value, pd.Timestamp):
        return value
    try:
        return pd.Timestamp(str(value))
    except Exception:
        return pd.NaT


def _safe_days(end_date, start_date) -> "int | None":
    """
    Return (end_date - start_date).days, clamped to >= 0.
    Returns None if either date is NaT/None.
    """
    if pd.isna(end_date) or pd.isna(start_date):
        return None
    delta = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days
    if delta < 0:
        log.debug("Negative day delta detected (%d) — clamping to 0.", delta)
        return 0
    return delta


def _quality_score(
    converted_to_account: int,
    converted_to_sale: int,
    converted_to_installation: int,
    days_to_account: "int | None",
) -> float:
    """
    Compute a composite lead quality score in [0.0, 1.0].

    Weights:
        40%  — converted to account
        30%  — converted to sale
        20%  — converted to installation
        10%  — speed-to-account bonus (decays linearly over SPEED_DECAY_DAYS)
    """
    score = (
        WEIGHT_ACCOUNT      * converted_to_account
        + WEIGHT_SALE         * converted_to_sale
        + WEIGHT_INSTALLATION * converted_to_installation
    )
    if days_to_account is not None:
        speed_bonus = WEIGHT_SPEED * max(0.0, 1.0 - days_to_account / SPEED_DECAY_DAYS)
        score += speed_bonus
    return round(min(score, 1.0), 6)


# ---------------------------------------------------------------------------
# Extract
# ---------------------------------------------------------------------------

def extract(source_path: Path) -> dict[str, pd.DataFrame]:
    """Load all relevant sheets from the Excel workbook into DataFrames."""
    log.info("Reading workbook: %s", source_path)
    sheets = ["Leads", "Accounts", "Sales", "Installations", "Customers"]
    data = pd.read_excel(source_path, sheet_name=sheets, engine="openpyxl")
    for name, df in data.items():
        log.info("  %-15s → %d rows, %d cols", name, len(df), len(df.columns))
    return data


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------

def transform(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Join source sheets and derive all columns for fact_lead_funnel.

    Returns a DataFrame ready to be inserted into ClickHouse.
    """
    leads         = sheets["Leads"].copy()
    accounts      = sheets["Accounts"].copy()
    sales         = sheets["Sales"].copy()
    installations = sheets["Installations"].copy()
    customers     = sheets["Customers"].copy()

    # ------------------------------------------------------------------
    # Normalise column names → snake_case
    # ------------------------------------------------------------------
    leads.columns         = leads.columns.str.strip().str.lower()
    accounts.columns      = accounts.columns.str.strip().str.lower()
    sales.columns         = sales.columns.str.strip().str.lower()
    installations.columns = installations.columns.str.strip().str.lower()
    customers.columns     = customers.columns.str.strip().str.lower()

    log.info("Leads columns:         %s", list(leads.columns))
    log.info("Accounts columns:      %s", list(accounts.columns))
    log.info("Sales columns:         %s", list(sales.columns))
    log.info("Installations columns: %s", list(installations.columns))
    log.info("Customers columns:     %s", list(customers.columns))

    # ------------------------------------------------------------------
    # Parse date columns
    # ------------------------------------------------------------------
    leads["created_at"]              = pd.to_datetime(leads["created_at"],         errors="coerce")
    accounts["created_at"]           = pd.to_datetime(accounts["created_at"],      errors="coerce")
    sales["sale_date"]               = pd.to_datetime(sales["sale_date"],           errors="coerce")
    installations["installation_date"] = pd.to_datetime(installations["installation_date"], errors="coerce")

    # ------------------------------------------------------------------
    # Step 1 — Enrich leads with account data (left join on lead_id)
    # ------------------------------------------------------------------
    accounts_slim = accounts[[
        "lead_id", "id", "agent_id", "installation_id", "created_at"
    ]].rename(columns={
        "id":         "account_id",
        "agent_id":   "employee_id",
        "created_at": "account_created_at",
    })

    df = leads.merge(accounts_slim, left_on="id", right_on="lead_id", how="left")

    # ------------------------------------------------------------------
    # Step 2 — Enrich with sale data (left join on account_id)
    # ------------------------------------------------------------------
    sales_slim = sales[["account_id", "sale_date"]].rename(
        columns={"account_id": "sale_account_id"}
    )
    df = df.merge(sales_slim, left_on="account_id", right_on="sale_account_id", how="left")

    # ------------------------------------------------------------------
    # Step 3 — Enrich with installation data (left join on installation_id)
    # ------------------------------------------------------------------
    installations_slim = installations[["id", "installation_date"]].rename(
        columns={"id": "inst_id"}
    )
    df = df.merge(
        installations_slim, left_on="installation_id", right_on="inst_id", how="left"
    )

    # ------------------------------------------------------------------
    # Step 4 — Enrich with customer region (for country_id)
    # ------------------------------------------------------------------
    customers_slim = customers[["id", "region"]].rename(
        columns={"id": "cust_id"}
    )
    df = df.merge(customers_slim, left_on="customer_id", right_on="cust_id", how="left")

    # ------------------------------------------------------------------
    # Step 5 — Derive fact columns
    # ------------------------------------------------------------------

    # lead_id: strip 'LEAD-' prefix → UInt64
    df["lead_id"] = (
        df["id"].str.replace("LEAD-", "", regex=False).astype("Int64")
    )

    # lead_created_date
    df["lead_created_date"] = df["created_at"].dt.date

    # Conversion flags
    df["converted_to_account"]      = df["account_id"].notna().astype("uint8")
    df["converted_to_sale"]         = df["sale_date"].notna().astype("uint8")
    df["converted_to_installation"] = df["installation_date"].notna().astype("uint8")

    # Days metrics
    df["days_to_account"] = df.apply(
        lambda r: _safe_days(r["account_created_at"], r["created_at"]), axis=1
    )
    df["days_to_sale"] = df.apply(
        lambda r: _safe_days(r["sale_date"], r["created_at"]), axis=1
    )
    df["days_to_installation"] = df.apply(
        lambda r: _safe_days(r["installation_date"], r["created_at"]), axis=1
    )

    # Dimension surrogate keys
    df["lead_source_id"] = (
        df["source"].map(LEAD_SOURCE_MAP).fillna(0).astype("uint32")
    )
    df["country_id"] = (
        df["region"].str.lower().map(COUNTRY_MAP).fillna(0).astype("uint32")
    )

    # customer_id: fill missing source nulls with empty string and warn
    null_cust_count = df["customer_id"].isna().sum()
    if null_cust_count > 0:
        log.warning(
            "%d lead(s) have a null customer_id in the source data — filling with ''",
            null_cust_count,
        )
    df["customer_id"] = df["customer_id"].fillna("").astype(str)

    # employee_id: fill missing (no account) with empty string
    df["employee_id"] = df["employee_id"].fillna("").astype(str)

    # Lead quality score
    df["lead_quality_score"] = df.apply(
        lambda r: _quality_score(
            r["converted_to_account"],
            r["converted_to_sale"],
            r["converted_to_installation"],
            r["days_to_account"],
        ),
        axis=1,
    ).astype("float32")

    # ETL load timestamp
    df["created_at_fact"] = datetime.now(timezone.utc).replace(tzinfo=None)

    # ------------------------------------------------------------------
    # Step 6 — Select and rename to match ClickHouse schema
    # ------------------------------------------------------------------
    fact = df[[
        "lead_id",
        "customer_id",
        "lead_source_id",
        "employee_id",
        "country_id",
        "lead_created_date",
        "converted_to_account",
        "converted_to_sale",
        "converted_to_installation",
        "days_to_account",
        "days_to_sale",
        "days_to_installation",
        "lead_quality_score",
        "created_at_fact",
    ]].rename(columns={"created_at_fact": "created_at"})

    # ------------------------------------------------------------------
    # Step 7 — Data quality report
    # ------------------------------------------------------------------
    _log_quality_report(fact)

    return fact


def _log_quality_report(df: pd.DataFrame) -> None:
    """Log a concise summary of the transformed DataFrame."""
    n = len(df)
    log.info("=" * 60)
    log.info("TRANSFORM SUMMARY")
    log.info("=" * 60)
    log.info("Total rows:                  %d", n)
    log.info("Converted to account:        %d (%.1f%%)", df["converted_to_account"].sum(),
             df["converted_to_account"].mean() * 100)
    log.info("Converted to sale:           %d (%.1f%%)", df["converted_to_sale"].sum(),
             df["converted_to_sale"].mean() * 100)
    log.info("Converted to installation:   %d (%.1f%%)", df["converted_to_installation"].sum(),
             df["converted_to_installation"].mean() * 100)
    log.info("Unknown lead source (id=0):  %d", (df["lead_source_id"] == 0).sum())
    log.info("Unknown country (id=0):      %d", (df["country_id"] == 0).sum())
    log.info("Missing employee_id:         %d", (df["employee_id"] == "").sum())
    neg_acc  = df["days_to_account"].dropna()
    neg_sale = df["days_to_sale"].dropna()
    log.info("Negative days clamped (acct):%d", (neg_acc == 0).sum())
    log.info("Avg lead quality score:      %.4f", df["lead_quality_score"].mean())
    log.info("=" * 60)


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------

def validate(df: pd.DataFrame) -> bool:
    """
    Run pre-load assertions. Returns True if all pass, False otherwise.
    Logs each failing check but does NOT raise — caller decides whether to abort.
    """
    passed = True

    def _check(condition: bool, msg: str) -> None:
        nonlocal passed
        if not condition:
            log.error("VALIDATION FAILED: %s", msg)
            passed = False
        else:
            log.info("VALIDATION OK:     %s", msg)

    _check(df["lead_id"].notna().all(),              "No null lead_ids")
    _check(df["lead_id"].nunique() == len(df),       "lead_id is unique per row")
    _check(df["lead_created_date"].notna().all(),     "No null lead_created_date")

    # customer_id nulls are a source data quality issue — warn but don't fail
    null_cust = (df["customer_id"] == "").sum()
    if null_cust > 0:
        log.warning("VALIDATION WARN:   %d row(s) have empty customer_id (source data nulls)", null_cust)
    else:
        log.info("VALIDATION OK:     All customer_ids populated")
    _check(df["converted_to_account"].isin([0, 1]).all(),      "converted_to_account is 0/1")
    _check(df["converted_to_sale"].isin([0, 1]).all(),         "converted_to_sale is 0/1")
    _check(df["converted_to_installation"].isin([0, 1]).all(), "converted_to_installation is 0/1")
    _check(
        df["lead_quality_score"].between(0.0, 1.0).all(),
        "lead_quality_score in [0, 1]",
    )
    _check(
        (df["days_to_account"].dropna() >= 0).all(),
        "days_to_account non-negative",
    )
    _check(
        (df["days_to_sale"].dropna() >= 0).all(),
        "days_to_sale non-negative",
    )
    _check(
        (df["days_to_installation"].dropna() >= 0).all(),
        "days_to_installation non-negative",
    )

    return passed


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load(df: pd.DataFrame, dry_run: bool = False) -> None:
    """
    Insert the transformed DataFrame into ClickHouse.

    Uses clickhouse-connect (HTTP-based, no native driver needed).
    Falls back to printing a CSV preview on dry-run.
    """
    if dry_run:
        log.info("DRY RUN — skipping ClickHouse insert.")
        preview_path = PROJECT_ROOT / "data" / "interim" / "fact_lead_funnel_preview.csv"
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(preview_path, index=False)
        log.info("Preview written to: %s", preview_path)
        return

    try:
        import clickhouse_connect  # type: ignore
    except ImportError:
        log.error(
            "clickhouse-connect is not installed.\n"
            "  Run:  pip install clickhouse-connect\n"
            "  Then rerun this script."
        )
        sys.exit(1)

    log.info(
        "Connecting to ClickHouse at %s:%d  db=%s  user=%s",
        CH_HOST, CH_PORT, CH_DB, CH_USER,
    )
    client = clickhouse_connect.get_client(
        host=CH_HOST,
        port=CH_PORT,
        username=CH_USER,
        password=CH_PASSWORD,
        database=CH_DB,
    )

    # Prepare column types that ClickHouse expects
    # Nullable integers must be sent as Python None, not NaN
    nullable_int_cols = ["days_to_account", "days_to_sale", "days_to_installation"]
    for col in nullable_int_cols:
        df[col] = df[col].where(df[col].notna(), other=None)

    log.info("Inserting %d rows into %s.%s …", len(df), CH_DB, TARGET_TABLE)
    client.insert_df(TARGET_TABLE, df)
    log.info("Insert complete.")

    # Verify row count
    result = client.query(f"SELECT count() FROM {TARGET_TABLE}")
    count  = result.first_row[0]
    log.info("Row count in %s after insert: %d", TARGET_TABLE, count)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Populate fact_lead_funnel in ClickHouse from the raw Excel workbook."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Path to the source Excel file (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Transform only — write CSV preview, skip ClickHouse insert.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip pre-load validation checks.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    log.info("=" * 60)
    log.info("populate_fact_lead_funnel  |  %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("Source:   %s", args.source)
    log.info("Dry run:  %s", args.dry_run)
    log.info("=" * 60)

    # 1. Extract
    sheets = extract(args.source)

    # 2. Transform
    fact_df = transform(sheets)

    # 3. Validate
    if not args.skip_validation:
        ok = validate(fact_df)
        if not ok:
            log.error("Validation errors found. Aborting load. Fix issues or pass --skip-validation.")
            sys.exit(1)

    # 4. Load
    load(fact_df, dry_run=args.dry_run)

    log.info("Done.")


if __name__ == "__main__":
    main()
