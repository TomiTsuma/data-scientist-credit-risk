from clickhouse_driver import Client
import pandas as pd
import numpy as np

def run_report():
    client = Client(
        host="localhost",
        port=9000,
        user="clickhouse_user",
        password="clickhouse_password"
    )
    
    # Country mapping
    countries_raw = client.execute("SELECT country_id, country_name FROM sunculture_db.dim_country")
    country_map = {row[0]: row[1] for row in countries_raw}
    
    # 1. Commercial Growth (Sales by Quarter and Country)
    print("================ 1. SALES BY QUARTER & COUNTRY ================")
    query_sales = """
        SELECT 
            country_id,
            toStartOfQuarter(sale_date) as quarter,
            count() as sales_count
        FROM sunculture_db.fact_sales
        GROUP BY country_id, quarter
        ORDER BY quarter, country_id
    """
    df_sales = pd.DataFrame(client.execute(query_sales), columns=['country_id', 'quarter', 'sales_count'])
    df_sales['country_name'] = df_sales['country_id'].map(country_map)
    pivot_sales = df_sales.pivot(index='quarter', columns='country_name', values='sales_count').fillna(0)
    print(pivot_sales)
    
    # Calculate QoQ growth rate
    print("\nQoQ Growth Rates (%):")
    print(pivot_sales.pct_change() * 100)
    
    # 2. Conversion Funnel (Leads, Sales, Conversions by Country)
    print("\n================ 2. LEAD CONVERSIONS & QUALITY BY COUNTRY ================")
    query_leads = """
        SELECT 
            dc.country_id as country_id,
            count(flf.lead_id) as total_leads,
            sum(flf.converted_to_sale) as total_sales_from_leads,
            avg(flf.lead_quality_score) as avg_quality_score,
            avg(flf.days_to_sale) as avg_days_to_sale
        FROM sunculture_db.fact_lead_funnel flf
        JOIN sunculture_db.dim_customer dc ON flf.customer_id = dc.customer_id
        GROUP BY dc.country_id
    """
    df_leads = pd.DataFrame(client.execute(query_leads), columns=['country_id', 'total_leads', 'sales_from_leads', 'avg_quality', 'avg_days_to_sale'])
    df_leads['country_name'] = df_leads['country_id'].map(country_map)
    df_leads['conversion_rate'] = (df_leads['sales_from_leads'] / df_leads['total_leads']) * 100
    print(df_leads[['country_name', 'total_leads', 'sales_from_leads', 'conversion_rate', 'avg_quality', 'avg_days_to_sale']])
    
    # 3. Operational Inefficiencies - Installation Backlog by Country
    # Sales that are not in fact_installations
    print("\n================ 3. INSTALLATION BACKLOG BY COUNTRY ================")
    query_backlog = """
        SELECT 
            fs.country_id,
            count() as uninstalled_sales
        FROM sunculture_db.fact_sales fs
        LEFT JOIN sunculture_db.fact_installations fi ON fs.account_id = fi.account_id
        WHERE fi.installation_id IS NULL
        GROUP BY fs.country_id
    """
    df_backlog = pd.DataFrame(client.execute(query_backlog), columns=['country_id', 'uninstalled_sales'])
    df_backlog['country_name'] = df_backlog['country_id'].map(country_map)
    print(df_backlog[['country_name', 'uninstalled_sales']])
    
    # 4. Installation Delays
    # We filter for positive delays to understand the actual fulfillment duration for valid records
    print("\n================ 4. INSTALLATION DELAYS (VALID RECORDS) ================")
    query_delays = """
        SELECT 
            country_id,
            avg(dateDiff('day', sale_date, installation_date)) as avg_delay,
            median(dateDiff('day', sale_date, installation_date)) as median_delay,
            count() as installed_count
        FROM sunculture_db.fact_installations
        WHERE dateDiff('day', sale_date, installation_date) >= 0
        GROUP BY country_id
    """
    df_delays = pd.DataFrame(client.execute(query_delays), columns=['country_id', 'avg_delay', 'median_delay', 'installed_count'])
    df_delays['country_name'] = df_delays['country_id'].map(country_map)
    print(df_delays[['country_name', 'installed_count', 'avg_delay', 'median_delay']])
    
    # Print negative delay count
    query_neg = """
        SELECT 
            country_id,
            sum(dateDiff('day', sale_date, installation_date) < 0) as negative_delays_count,
            count() as total_count
        FROM sunculture_db.fact_installations
        GROUP BY country_id
    """
    df_neg = pd.DataFrame(client.execute(query_neg), columns=['country_id', 'negative_delays', 'total'])
    df_neg['country_name'] = df_neg['country_id'].map(country_map)
    df_neg['pct_negative'] = (df_neg['negative_delays'] / df_neg['total']) * 100
    print("\nAnomaly: Negative Installation Delays by Country (Installation before Sale):")
    print(df_neg[['country_name', 'negative_delays', 'total', 'pct_negative']])

    # 5. Credit Risk & Account Health
    print("\n================ 5. CREDIT RISK BY COUNTRY ================")
    query_risk = """
        SELECT 
            country_id,
            count() as total_accounts,
            sum(is_currently_in_arrears) as in_arrears,
            avg(account_age_days) as avg_account_age
        FROM sunculture_db.fact_accounts_snapshots
        GROUP BY country_id
    """
    df_risk = pd.DataFrame(client.execute(query_risk), columns=['country_id', 'total_accounts', 'in_arrears', 'avg_account_age'])
    df_risk['country_name'] = df_risk['country_id'].map(country_map)
    df_risk['arrears_rate'] = (df_risk['in_arrears'] / df_risk['total_accounts']) * 100
    print(df_risk[['country_name', 'total_accounts', 'in_arrears', 'arrears_rate', 'avg_account_age']])

if __name__ == "__main__":
    run_report()
