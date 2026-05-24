from clickhouse_driver import Client
import pandas as pd

def inspect_details():
    client = Client(
        host="localhost",
        port=9000,
        user="clickhouse_user",
        password="clickhouse_password"
    )
    
    # 1. Lead funnel conversion statistics
    print("--- Lead Funnel Summary ---")
    query_leads = """
        SELECT 
            count() as total_rows,
            sum(converted_to_account) as sum_conv_acc,
            sum(converted_to_sale) as sum_conv_sale,
            sum(converted_to_installation) as sum_conv_inst,
            avg(lead_quality_score) as avg_quality,
            sum(lead_quality_score > 0) as positive_quality_count
        FROM sunculture_db.fact_lead_funnel
    """
    res = client.execute(query_leads)
    print("Lead Funnel Aggregates:", res)

    # Let's inspect lead conversion times
    print("\n--- Lead Funnel Conversion Times ---")
    query_times = """
        SELECT 
            avg(days_to_account) as avg_days_acc,
            avg(days_to_sale) as avg_days_sale,
            avg(days_to_dispatch) as avg_days_disp
        FROM sunculture_db.fact_lead_funnel
        WHERE converted_to_sale = 1
    """
    res_times = client.execute(query_times)
    print("Conversion times (days):", res_times)
    
    # Let's see some non-null values in fact_lead_funnel
    print("\n--- Sample fact_lead_funnel records (where converted_to_sale = 1) ---")
    query_sample = """
        SELECT 
            lead_id, customer_id, converted_to_account, converted_to_sale,
            days_to_account, days_to_sale, days_to_dispatch, lead_quality_score
        FROM sunculture_db.fact_lead_funnel
        WHERE converted_to_sale = 1
        LIMIT 5
    """
    df_sample = pd.DataFrame(client.execute(query_sample), columns=['lead_id', 'customer_id', 'converted_to_account', 'converted_to_sale', 'days_to_account', 'days_to_sale', 'days_to_dispatch', 'lead_quality_score'])
    print(df_sample)

    # 2. Inspecting the Sales vs Installations join
    print("\n--- Sales vs Installations ---")
    sales_count = client.execute("SELECT count() FROM sunculture_db.fact_sales")[0][0]
    inst_count = client.execute("SELECT count() FROM sunculture_db.fact_installations")[0][0]
    print(f"Sales count: {sales_count}, Installations count: {inst_count}")
    
    # Let's find accounts in fact_sales that don't have matching accounts in fact_installations
    query_mismatch = """
        SELECT count() 
        FROM sunculture_db.fact_sales
        WHERE account_id NOT IN (SELECT account_id FROM sunculture_db.fact_installations)
    """
    mismatch_count = client.execute(query_mismatch)[0][0]
    print(f"Sales account_ids not in fact_installations: {mismatch_count}")
    
    # Let's check if there are account_ids in fact_installations that don't match fact_sales
    query_mismatch_inst = """
        SELECT count() 
        FROM sunculture_db.fact_installations
        WHERE account_id NOT IN (SELECT account_id FROM sunculture_db.fact_sales)
    """
    mismatch_inst_count = client.execute(query_mismatch_inst)[0][0]
    print(f"Installations account_ids not in fact_sales: {mismatch_inst_count}")

    # 3. Account snapshots check
    print("\n--- Account Snapshot Age Details ---")
    query_age = """
        SELECT 
            min(account_age_days) as min_age,
            max(account_age_days) as max_age,
            avg(account_age_days) as avg_age,
            sum(account_age_days > 0) as non_zero_count,
            count() as total
        FROM sunculture_db.fact_accounts_snapshots
    """
    print(client.execute(query_age))

if __name__ == "__main__":
    inspect_details()
