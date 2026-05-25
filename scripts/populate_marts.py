"""
populate_marts.py
-----------------
Recreates and populates the three analytical marts in ClickHouse.
"""

from __future__ import annotations

import os

from clickhouse_driver import Client

CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", "9000"))
CH_USER = os.getenv("CLICKHOUSE_USER", "clickhouse_user")
CH_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "clickhouse_password")
DB = os.getenv("CLICKHOUSE_DB", "sunculture_db")


def get_client() -> Client:
    return Client(
        host=CH_HOST,
        port=CH_PORT,
        user=CH_USER,
        password=CH_PASSWORD,
    )


def populate_marts(client: Client | None = None) -> None:
    client = client or get_client()

    def exec_sql(sql: str, label: str = "") -> None:
        try:
            client.execute(sql)
            if label:
                print(f"  [OK]  {label}")
        except Exception as e:
            print(f"  [ERR] {label}: {str(e)[:400]}")

    tier_expr = "if(dp.refurb_status = 'Refurbished', 'Refurbished', 'New')"

    print("\n[marts] Dropping existing mart tables...")
    for mart in [
        "mart_customer_account_analytics",
        "mart_sales_performance",
        "mart_installation_operations",
    ]:
        exec_sql(f"DROP TABLE IF EXISTS {DB}.{mart}", f"DROP {mart}")

    print("[marts] mart_customer_account_analytics...")
    exec_sql(
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
    exec_sql(
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
            {tier_expr} AS product_tier,
            fa.account_status_id,
            das.account_status_name AS account_status,
            das.risk_category,
            fa.payment_type,
            fa.is_currently_in_arrears AS is_in_arrears,
            fa.account_age_days,
            fa.activation_date,
            fa.created_at
        FROM {DB}.fact_accounts_snapshots fa
        LEFT JOIN {DB}.dim_customer cust ON fa.customer_id = cust.customer_id
        LEFT JOIN {DB}.dim_country dc ON fa.country_id = dc.country_id
        LEFT JOIN {DB}.dim_product dp ON fa.product_id = dp.product_id
        LEFT JOIN {DB}.dim_account_status das ON fa.account_status_id = das.account_status_id
        """,
        "INSERT mart_customer_account_analytics",
    )

    print("[marts] mart_sales_performance...")
    exec_sql(
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
    exec_sql(
        f"""
        INSERT INTO {DB}.mart_sales_performance
        SELECT
            fs.sale_id,
            fs.sale_date,
            fs.country_id,
            dc.country_name,
            fs.product_id,
            dp.product_name,
            {tier_expr} AS product_tier,
            fs.lead_source_id,
            dls.lead_source_name,
            fs.agent_id,
            COALESCE(de.full_name, '') AS agent_name,
            fs.account_id,
            fs.customer_id,
            fs.account_type,
            fs.account_status,
            '' AS payment_type,
            fs.created_at
        FROM {DB}.fact_sales fs
        LEFT JOIN {DB}.dim_country dc ON fs.country_id = dc.country_id
        LEFT JOIN {DB}.dim_product dp ON fs.product_id = dp.product_id
        LEFT JOIN {DB}.dim_lead_source dls ON fs.lead_source_id = dls.lead_source_id
        LEFT JOIN {DB}.dim_employee de ON fs.agent_id = de.employee_id
        """,
        "INSERT mart_sales_performance",
    )

    print("[marts] mart_installation_operations...")
    exec_sql(
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
    exec_sql(
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
            {tier_expr} AS product_tier,
            fi.engineer_id,
            COALESCE(de.full_name, '') AS installer_name,
            COALESCE(dd.department_name, '') AS installer_department,
            fi.sale_date,
            fi.installation_date,
            toInt32(dateDiff('day', fi.sale_date, fi.installation_date)) AS installation_delay_days,
            fi.installation_status,
            fi.created_at
        FROM {DB}.fact_installations fi
        LEFT JOIN {DB}.dim_country dc ON fi.country_id = dc.country_id
        LEFT JOIN {DB}.dim_product dp ON fi.product_id = dp.product_id
        LEFT JOIN {DB}.dim_employee de ON fi.engineer_id = de.employee_id
        LEFT JOIN {DB}.dim_department dd ON de.department_id = dd.department_id
        """,
        "INSERT mart_installation_operations",
    )

    print("MART POPULATION COMPLETE:")
    for mart in [
        "mart_customer_account_analytics",
        "mart_sales_performance",
        "mart_installation_operations",
    ]:
        n = client.execute(f"SELECT count() FROM {DB}.{mart}")[0][0]
        print(f"  {mart}: {n:,} rows")


if __name__ == "__main__":
    populate_marts()
