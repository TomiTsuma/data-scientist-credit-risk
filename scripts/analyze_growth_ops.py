from clickhouse_driver import Client
import pandas as pd
import numpy as np

def run_analysis():
    client = Client(
        host="localhost",
        port=9000,
        user="clickhouse_user",
        password="clickhouse_password"
    )
    
    # Get country map first to map country_id to country_name
    countries_raw = client.execute("SELECT country_id, country_name FROM sunculture_db.dim_country")
    country_map = {row[0]: row[1] for row in countries_raw}
    print("Country mapping:", country_map)
    
    # 1. Date ranges in key tables
    print("\n--- Date Ranges ---")
    sales_dates = client.execute("SELECT min(sale_date), max(sale_date) FROM sunculture_db.fact_sales")[0]
    inst_dates = client.execute("SELECT min(sale_date), max(sale_date), min(installation_date), max(installation_date) FROM sunculture_db.fact_installations")[0]
    lead_dates = client.execute("SELECT min(lead_created_date), max(lead_created_date) FROM sunculture_db.fact_lead_funnel")[0]
    print(f"Sales date range: {sales_dates[0]} to {sales_dates[1]}")
    print(f"Installations sale date range: {inst_dates[0]} to {inst_dates[1]}")
    print(f"Installations installation date range: {inst_dates[2]} to {inst_dates[3]}")
    print(f"Leads date range: {lead_dates[0]} to {lead_dates[1]}")
    
    # 2. Sales growth over time by country
    print("\n--- Monthly Sales by Country ---")
    sales_query = """
        SELECT 
            country_id,
            toStartOfMonth(sale_date) as month,
            count() as sales_count
        FROM sunculture_db.fact_sales
        GROUP BY country_id, month
        ORDER BY country_id, month
    """
    sales_data = client.execute(sales_query)
    df_sales = pd.DataFrame(sales_data, columns=['country_id', 'month', 'sales_count'])
    df_sales['country_name'] = df_sales['country_id'].map(country_map)
    
    # Pivot for readability
    pivot_sales = df_sales.pivot(index='month', columns='country_name', values='sales_count').fillna(0)
    print(pivot_sales)
    
    # 3. Installation delays over time by country
    print("\n--- Average Installation Delay (Days) by Country ---")
    delay_query = """
        SELECT 
            country_id,
            toStartOfMonth(sale_date) as month,
            avg(dateDiff('day', sale_date, installation_date)) as avg_delay,
            count() as installed_count
        FROM sunculture_db.fact_installations
        WHERE installation_status = 'Installed' OR installation_date IS NOT NULL
        GROUP BY country_id, month
        ORDER BY country_id, month
    """
    delay_data = client.execute(delay_query)
    df_delay = pd.DataFrame(delay_data, columns=['country_id', 'month', 'avg_delay', 'installed_count'])
    df_delay['country_name'] = df_delay['country_id'].map(country_map)
    
    pivot_delay = df_delay.pivot(index='month', columns='country_name', values='avg_delay').fillna(0)
    print(pivot_delay)
    
    # 4. Installation statuses by country
    print("\n--- Installation Status by Country ---")
    status_query = """
        SELECT 
            country_id,
            installation_status,
            count() as count
        FROM sunculture_db.fact_installations
        GROUP BY country_id, installation_status
        ORDER BY country_id, installation_status
    """
    status_data = client.execute(status_query)
    df_status = pd.DataFrame(status_data, columns=['country_id', 'installation_status', 'count'])
    df_status['country_name'] = df_status['country_id'].map(country_map)
    pivot_status = df_status.pivot(index='installation_status', columns='country_name', values='count').fillna(0)
    print(pivot_status)

    # 5. Accounts: payment type and arrears status by country
    print("\n--- Accounts Snapshot details by Country ---")
    accounts_query = """
        SELECT 
            country_id,
            is_currently_in_arrears,
            count() as count
        FROM sunculture_db.fact_accounts_snapshots
        GROUP BY country_id, is_currently_in_arrears
    """
    accounts_data = client.execute(accounts_query)
    df_accounts = pd.DataFrame(accounts_data, columns=['country_id', 'is_currently_in_arrears', 'count'])
    df_accounts['country_name'] = df_accounts['country_id'].map(country_map)
    pivot_accounts = df_accounts.pivot(index='is_currently_in_arrears', columns='country_name', values='count').fillna(0)
    print(pivot_accounts)

if __name__ == "__main__":
    run_analysis()
