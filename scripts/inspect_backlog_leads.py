from clickhouse_driver import Client
import pandas as pd

def analyze_backlog_leads():
    client = Client(
        host="localhost",
        port=9000,
        user="clickhouse_user",
        password="clickhouse_password"
    )
    
    countries_raw = client.execute("SELECT country_id, country_name FROM sunculture_db.dim_country")
    country_map = {row[0]: row[1] for row in countries_raw}

    # 1. Backlog country breakdown
    print("--- Backlog (Uninstalled Sales) by Country ---")
    query_backlog = """
        SELECT 
            fs.country_id,
            count() as uninstalled_count
        FROM sunculture_db.fact_sales fs
        LEFT JOIN sunculture_db.fact_installations fi ON fs.account_id = fi.account_id
        WHERE fi.installation_id IS NULL
        GROUP BY fs.country_id
    """
    res_backlog = client.execute(query_backlog)
    for row in res_backlog:
        print(f" - {country_map.get(row[0], 'Unknown')}: {row[1]} uninstalled sales")

    # 2. Lead funnel times without sentinel values
    print("\n--- Lead Funnel Validation (Excluding 99999 Sentinel) ---")
    
    for metric in ['days_to_account', 'days_to_sale', 'days_to_dispatch']:
        query_metric = f"""
            SELECT 
                dc.country_id,
                count() as total_records,
                sum({metric} = 99999) as sentinel_count,
                sum({metric} != 99999) as valid_count,
                avg(NULLIF({metric}, 99999)) as avg_valid_days,
                median(NULLIF({metric}, 99999)) as median_valid_days
            FROM sunculture_db.fact_lead_funnel flf
            JOIN sunculture_db.dim_customer dc ON flf.customer_id = dc.customer_id
            GROUP BY dc.country_id
        """
        res_metric = client.execute(query_metric)
        print(f"\nMetric: {metric}")
        for row in res_metric:
            country = country_map.get(row[0], 'Unknown')
            print(f" - {country}: Total={row[1]}, Sentinels={row[2]} ({row[2]/row[1]*100:.1f}%), Valids={row[3]}, Avg={row[4]:.2f} days, Median={row[5]:.1f} days")

    # 3. Product adoption and arrears by country
    print("\n--- Product Sales and Arrears ---")
    query_prod_arrears = """
        SELECT 
            country_id,
            product_id,
            count() as total,
            sum(is_currently_in_arrears) as in_arrears
        FROM sunculture_db.fact_accounts_snapshots
        GROUP BY country_id, product_id
        ORDER BY country_id, total DESC
    """
    res_prod = client.execute(query_prod_arrears)
    df_prod = pd.DataFrame(res_prod, columns=['country_id', 'product_id', 'total', 'in_arrears'])
    df_prod['country_name'] = df_prod['country_id'].map(country_map)
    
    # Get product names from dim_product
    prod_raw = client.execute("SELECT product_id, product_name FROM sunculture_db.dim_product")
    prod_map = {row[0]: row[1] for row in prod_raw}
    df_prod['product_name'] = df_prod['product_id'].map(prod_map)
    df_prod['arrears_rate'] = (df_prod['in_arrears'] / df_prod['total']) * 100
    
    print(df_prod[['country_name', 'product_name', 'total', 'in_arrears', 'arrears_rate']].head(15))

if __name__ == "__main__":
    analyze_backlog_leads()
