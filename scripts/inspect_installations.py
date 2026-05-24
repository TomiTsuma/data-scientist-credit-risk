from clickhouse_driver import Client
import pandas as pd

def inspect_installations():
    client = Client(
        host="localhost",
        port=9000,
        user="clickhouse_user",
        password="clickhouse_password"
    )
    
    print("--- SAMPLE FROM fact_installations ---")
    query = """
        SELECT 
            installation_id,
            customer_id,
            sale_date,
            installation_date,
            installation_status,
            dateDiff('day', sale_date, installation_date) as delay
        FROM sunculture_db.fact_installations
        LIMIT 10
    """
    res = client.execute(query)
    df = pd.DataFrame(res, columns=['installation_id', 'customer_id', 'sale_date', 'installation_date', 'installation_status', 'delay'])
    print(df)
    
    print("\n--- Summary of delays ---")
    query_delays = """
        SELECT 
            count() as total,
            sum(sale_date > installation_date) as sale_after_install,
            sum(sale_date = installation_date) as sale_equals_install,
            sum(sale_date < installation_date) as sale_before_install
        FROM sunculture_db.fact_installations
    """
    print(client.execute(query_delays))

if __name__ == "__main__":
    inspect_installations()
