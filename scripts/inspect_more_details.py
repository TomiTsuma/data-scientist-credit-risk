from clickhouse_driver import Client
import pandas as pd

def inspect_more():
    client = Client(
        host="localhost",
        port=9000,
        user="clickhouse_user",
        password="clickhouse_password"
    )
    
    countries_raw = client.execute("SELECT country_id, country_name FROM sunculture_db.dim_country")
    country_map = {row[0]: row[1] for row in countries_raw}

    # 1. Backlog country breakdown with fi.installation_id = ''
    print("--- Backlog (Uninstalled Sales) by Country (using empty string check) ---")
    query_backlog = """
        SELECT 
            fs.country_id,
            count() as uninstalled_count
        FROM sunculture_db.fact_sales fs
        LEFT JOIN sunculture_db.fact_installations fi ON fs.account_id = fi.account_id
        WHERE fi.installation_id = ''
        GROUP BY fs.country_id
    """
    res_backlog = client.execute(query_backlog)
    for row in res_backlog:
        print(f" - {country_map.get(row[0], 'Unknown')}: {row[1]} uninstalled sales")

    # 2. Product and Arrears rates across ALL countries
    print("\n--- Product Sales and Arrears across all countries ---")
    query_prod = """
        SELECT 
            country_id,
            product_id,
            count() as total,
            sum(is_currently_in_arrears) as in_arrears
        FROM sunculture_db.fact_accounts_snapshots
        GROUP BY country_id, product_id
        ORDER BY country_id, total DESC
    """
    res_prod = client.execute(query_prod)
    df_prod = pd.DataFrame(res_prod, columns=['country_id', 'product_id', 'total', 'in_arrears'])
    df_prod['country_name'] = df_prod['country_id'].map(country_map)
    
    prod_raw = client.execute("SELECT product_id, product_name FROM sunculture_db.dim_product")
    prod_map = {row[0]: row[1] for row in prod_raw}
    df_prod['product_name'] = df_prod['product_id'].map(prod_map)
    df_prod['arrears_rate'] = (df_prod['in_arrears'] / df_prod['total']) * 100
    
    pd.set_option('display.max_rows', 100)
    print(df_prod[['country_name', 'product_name', 'total', 'in_arrears', 'arrears_rate']])

    # 3. Check lead quality scores in fact_lead_funnel
    print("\n--- Lead Quality Score Stats ---")
    res_lq = client.execute("SELECT min(lead_quality_score), max(lead_quality_score), avg(lead_quality_score), count() FROM sunculture_db.fact_lead_funnel")
    print("Min, Max, Avg, Count:", res_lq)

if __name__ == "__main__":
    inspect_more()
