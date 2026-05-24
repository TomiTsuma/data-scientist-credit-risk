from clickhouse_driver import Client
import pandas as pd

client = Client(
    host="localhost",
    port=9000,
    user="clickhouse_user",
    password="clickhouse_password"
)

tables = [
    "fact_sales",
    "fact_installations",
    "fact_accounts_snapshots",
    "dim_customer",
    "dim_country",
    "dim_product",
    "dim_account_status",
    "dim_lead_source",
    "dim_employee",
    "dim_department",
    "mart_customer_account_analytics",
    "mart_sales_performance",
    "mart_installation_operations",
]

for t in tables:
    print(f"\n{'='*60}")
    print(f"TABLE: {t}")
    print(f"{'='*60}")
    try:
        cols = client.execute(f"DESCRIBE sunculture_db.{t}")
        for c in cols:
            print(f"  {c[0]:40s}  {c[1]}")
        row_count = client.execute(f"SELECT count() FROM sunculture_db.{t}")[0][0]
        print(f"  --> Row count: {row_count}")
    except Exception as e:
        print(f"  ERROR: {e}")
