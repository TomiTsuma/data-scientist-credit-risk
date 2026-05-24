from clickhouse_driver import Client
import pandas as pd

def inspect():
    try:
        client = Client(
            host="localhost",
            port=9000,
            user="clickhouse_user",
            password="clickhouse_password"
        )
        print("Connected successfully to ClickHouse!")
        print("Version:", client.execute("SELECT version()")[0][0])
        
        print("\nDatabases:")
        for db in client.execute("SHOW DATABASES"):
            print(f" - {db[0]}")
            
        print("\nTables in sunculture_db:")
        tables = client.execute("SHOW TABLES FROM sunculture_db")
        for table in tables:
            table_name = table[0]
            count = client.execute(f"SELECT count() FROM sunculture_db.{table_name}")[0][0]
            print(f" - {table_name}: {count} rows")
            
    except Exception as e:
        print("Error connecting to ClickHouse:", e)

if __name__ == "__main__":
    inspect()
