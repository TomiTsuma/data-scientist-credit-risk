"""
populate_marts.py
-----------------
Recreates and populates the three analytical marts in ClickHouse:
  - mart_customer_account_analytics
  - mart_sales_performance
  - mart_installation_operations

Uses a two-step CREATE TABLE (explicit columns) + INSERT INTO ... SELECT
to avoid the ClickHouse CTAS column-resolution errors seen with the
previous approach.
"""

from clickhouse_driver import Client

client = Client(
    host="localhost",
    port=9000,
    user="clickhouse_user",
    password="clickhouse_password",
)

DB = "sunculture_db"


def exec(sql: str, label: str = "") -> None:
    try:
        client.execute(sql)
        if label:
            print(f"  [OK]  {label}")
    except Exception as e:
        print(f"  [ERR] {label}: {str(e)[:400]}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. DROP existing marts (safe re-run)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1/6] Dropping existing mart tables...")
for mart in [
    "mart_customer_account_analytics",
    "mart_sales_performance",
    "mart_installation_operations",
]:
    exec(f"DROP TABLE IF EXISTS {DB}.{mart}", f"DROP {mart}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. CREATE mart_customer_account_analytics
#    Source: fact_accounts_snapshots JOIN dim_customer, dim_country,
#            dim_product, dim_account_status
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2/6] Creating mart_customer_account_analytics...")
exec(
    f"""
    CREATE TABLE {DB}.mart_customer_account_analytics
    (
        account_id          String,
        customer_id         String,
        country_id          UUID,
        country_name        String,
        gender              String,
        age                 UInt8,
        age_bucket          String,
        product_id          String,
        product_name        String,
        product_tier        String,
        account_status_id   UUID,
        account_status      String,
        risk_category       String,
        payment_type        String,
        is_in_arrears       Bool,
        account_age_days    UInt32,
        activation_date     Date,
        created_at          DateTime
    )
    ENGINE = MergeTree()
    ORDER BY (country_id, customer_id)
    """,
    "CREATE mart_customer_account_analytics",
)

print("[3/6] Populating mart_customer_account_analytics...")
exec(
    f"""
    INSERT INTO {DB}.mart_customer_account_analytics
    SELECT
        fa.account_id,
        fa.customer_id,
        fa.country_id,
        dc.country_name,
        cust.gender,
        cust.age,
        cust.age_bucket,
        fa.product_id,
        dp.product_name,
        if(dp.refurb_status, 'Refurbished', 'New')  AS product_tier,
        fa.account_status_id,
        das.account_status_name                      AS account_status,
        das.risk_category,
        fa.payment_type,
        fa.is_currently_in_arrears                   AS is_in_arrears,
        fa.account_age_days,
        fa.activation_date,
        fa.created_at
    FROM {DB}.fact_accounts_snapshots fa
    LEFT JOIN {DB}.dim_customer        cust ON fa.customer_id      = cust.customer_id
    LEFT JOIN {DB}.dim_country         dc   ON fa.country_id       = dc.country_id
    LEFT JOIN {DB}.dim_product         dp   ON fa.product_id       = dp.product_id
    LEFT JOIN {DB}.dim_account_status  das  ON fa.account_status_id = das.account_status_id
    """,
    "INSERT mart_customer_account_analytics",
)

row_count = client.execute(
    f"SELECT count() FROM {DB}.mart_customer_account_analytics"
)[0][0]
print(f"  --> Rows inserted: {row_count:,}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. CREATE mart_sales_performance
#    Source: fact_sales JOIN dim_country, dim_product, dim_lead_source,
#            dim_employee (agent)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4/6] Creating mart_sales_performance...")
exec(
    f"""
    CREATE TABLE {DB}.mart_sales_performance
    (
        sale_id             String,
        sale_date           Date,
        country_id          UUID,
        country_name        String,
        product_id          String,
        product_name        String,
        product_tier        String,
        lead_source_id      UUID,
        lead_source_name    String,
        agent_id            String,
        agent_name          String,
        account_id          String,
        customer_id         String,
        account_type        String,
        account_status      String,
        payment_type        String,
        created_at          DateTime
    )
    ENGINE = MergeTree()
    ORDER BY (country_id, sale_date)
    """,
    "CREATE mart_sales_performance",
)

print("[5/6] Populating mart_sales_performance...")
exec(
    f"""
    INSERT INTO {DB}.mart_sales_performance
    SELECT
        fs.sale_id,
        fs.sale_date,
        fs.country_id,
        dc.country_name,
        fs.product_id,
        dp.product_name,
        if(dp.refurb_status, 'Refurbished', 'New')  AS product_tier,
        fs.lead_source_id,
        dls.lead_source_name,
        fs.agent_id,
        COALESCE(de.full_name, '')                   AS agent_name,
        fs.account_id,
        fs.customer_id,
        fs.account_type,
        fs.account_status,
        ''                                           AS payment_type,
        fs.created_at
    FROM {DB}.fact_sales fs
    LEFT JOIN {DB}.dim_country     dc  ON fs.country_id      = dc.country_id
    LEFT JOIN {DB}.dim_product     dp  ON fs.product_id      = dp.product_id
    LEFT JOIN {DB}.dim_lead_source dls ON fs.lead_source_id  = dls.lead_source_id
    LEFT JOIN {DB}.dim_employee    de  ON fs.agent_id        = de.employee_id
    """,
    "INSERT mart_sales_performance",
)

row_count = client.execute(
    f"SELECT count() FROM {DB}.mart_sales_performance"
)[0][0]
print(f"  --> Rows inserted: {row_count:,}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. CREATE mart_installation_operations
#    Source: fact_installations JOIN dim_country, dim_product, dim_employee,
#            dim_department
# ─────────────────────────────────────────────────────────────────────────────
print("\n[6/6] Creating & populating mart_installation_operations...")
exec(
    f"""
    CREATE TABLE {DB}.mart_installation_operations
    (
        installation_id         String,
        account_id              String,
        customer_id             String,
        country_id              UUID,
        country_name            String,
        product_id              String,
        product_name            String,
        product_tier            String,
        engineer_id             String,
        installer_name          String,
        installer_department    String,
        sale_date               Date,
        installation_date       Date,
        installation_delay_days Int32,
        installation_status     String,
        created_at              DateTime
    )
    ENGINE = MergeTree()
    ORDER BY (country_id, installation_date)
    """,
    "CREATE mart_installation_operations",
)

exec(
    f"""
    INSERT INTO {DB}.mart_installation_operations
    SELECT
        fi.installation_id,
        fi.account_id,
        fi.customer_id,
        fi.country_id,
        dc.country_name,
        fi.product_id,
        dp.product_name,
        if(dp.refurb_status, 'Refurbished', 'New')              AS product_tier,
        fi.engineer_id,
        COALESCE(de.full_name, '')                               AS installer_name,
        COALESCE(dd.department_name, '')                         AS installer_department,
        fi.sale_date,
        fi.installation_date,
        toInt32(dateDiff('day', fi.sale_date, fi.installation_date)) AS installation_delay_days,
        fi.installation_status,
        fi.created_at
    FROM {DB}.fact_installations fi
    LEFT JOIN {DB}.dim_country    dc ON fi.country_id  = dc.country_id
    LEFT JOIN {DB}.dim_product    dp ON fi.product_id  = dp.product_id
    LEFT JOIN {DB}.dim_employee   de ON fi.engineer_id = de.employee_id
    LEFT JOIN {DB}.dim_department dd ON de.department_id = dd.department_id
    """,
    "INSERT mart_installation_operations",
)

row_count = client.execute(
    f"SELECT count() FROM {DB}.mart_installation_operations"
)[0][0]
print(f"  --> Rows inserted: {row_count:,}")


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("MART POPULATION COMPLETE — Final counts:")
for mart in [
    "mart_customer_account_analytics",
    "mart_sales_performance",
    "mart_installation_operations",
]:
    n = client.execute(f"SELECT count() FROM {DB}.{mart}")[0][0]
    print(f"  {mart:<45s} {n:>8,} rows")
print("="*60)
