from clickhouse_driver import Client
import pandas as pd

def inspect_schemas():
    client = Client(
        host="localhost",
        port=9000,
        user="clickhouse_user",
        password="clickhouse_password"
    )
    
    # 1. Print schemas of important tables
    tables = [
        "dim_country",
        "fact_sales",
        "fact_installations",
        "fact_accounts_snapshots",
        "fact_lead_funnel"
    ]
    
    for table in tables:
        print(f"\n================ SCHEMA FOR {table} ================")
        desc = client.execute(f"DESCRIBE TABLE sunculture_db.{table}")
        for col in desc:
            print(f" - {col[0]}: {col[1]}")
            
    # 2. Print sample data from dim_country
    print("\n================ dim_country SAMPLE DATA ================")
    countries = client.execute("SELECT * FROM sunculture_db.dim_country")
    for row in countries:
        print(row)

if __name__ == "__main__":
    inspect_schemas()
